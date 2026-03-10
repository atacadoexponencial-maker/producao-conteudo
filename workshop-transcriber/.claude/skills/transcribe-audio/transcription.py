"""
Script de transcrição de áudio usando a API REST da AssemblyAI.

Uso via CLI:
    python .claude/skills/transcribe-audio/transcription.py <caminho-do-audio> [idioma]

Exemplo:
    python .claude/skills/transcribe-audio/transcription.py audio.mp3
    python .claude/skills/transcribe-audio/transcription.py audio.mp3 en
"""

import json
import os
import sys
import time
from pathlib import Path

import httpx

# Sobe 4 níveis para chegar à raiz do projeto:
# transcription.py → transcribe-audio/ → skills/ → .claude/ → projeto/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from shared.config import ASSEMBLYAI_API_KEY

BASE_URL = "https://api.assemblyai.com"


def _upload(audio_path: str, client: httpx.Client) -> str:
    """Faz upload do arquivo de áudio e retorna a URL gerada pela AssemblyAI."""
    with open(audio_path, "rb") as f:
        response = client.post(f"{BASE_URL}/v2/upload", content=f,
                               headers={"Content-Type": "application/octet-stream"},
                               timeout=300)
    response.raise_for_status()
    return response.json()["upload_url"]


def _submeter(upload_url: str, language: str, client: httpx.Client) -> str:
    """Submete o job de transcrição e retorna o transcript_id."""
    payload = {
        "audio_url": upload_url,
        "punctuate": True,
        "format_text": True,
        "speaker_labels": True,
        "speech_models": ["universal-2"],   # modelo exigido pela API atual
        "language_code": language,
    }
    response = client.post(f"{BASE_URL}/v2/transcript", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["id"]


def _aguardar(transcript_id: str, client: httpx.Client) -> dict:
    """Aguarda a conclusão da transcrição e retorna o resultado."""
    url = f"{BASE_URL}/v2/transcript/{transcript_id}"
    while True:
        response = client.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        status = data["status"]

        if status == "completed":
            return data
        if status == "error":
            raise RuntimeError(f"❌ Erro na transcrição: {data.get('error')}")

        time.sleep(5)   # verifica a cada 5 segundos


def transcribe(audio_path: str, language: str = "pt") -> dict:
    """
    Envia um arquivo de áudio para a AssemblyAI e retorna a transcrição completa.

    Args:
        audio_path: Caminho local para o arquivo de áudio.
        language:   Código do idioma (padrão: "pt" para português).

    Returns:
        Dicionário com:
          - text (str): transcrição em texto corrido
          - utterances (list[dict]): falas por locutor com start/end em ms
          - duration (float): duração total do áudio em segundos
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(
            f"❌ Arquivo de áudio não encontrado: {audio_path}"
        )

    headers = {"Authorization": ASSEMBLYAI_API_KEY}

    with httpx.Client(headers=headers) as client:
        try:
            print("⏫ Fazendo upload do áudio...", file=sys.stderr)
            upload_url = _upload(audio_path, client)

            print("📝 Submetendo para transcrição...", file=sys.stderr)
            transcript_id = _submeter(upload_url, language, client)

            print("⏳ Aguardando conclusão...", file=sys.stderr)
            data = _aguardar(transcript_id, client)

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                raise PermissionError(
                    "❌ Chave da AssemblyAI inválida. Verifique o .env"
                ) from exc
            raise RuntimeError(
                f"❌ Erro na transcrição: {exc.response.text}"
            ) from exc

    # Monta a lista de utterances (falas por locutor)
    utterances: list[dict] = []
    for u in data.get("utterances") or []:
        utterances.append({
            "speaker": u["speaker"],
            "start": u["start"],    # em milissegundos
            "end": u["end"],        # em milissegundos
            "text": u["text"],
        })

    return {
        "text": data.get("text") or "",
        "utterances": utterances,
        "duration": data.get("audio_duration") or 0,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python .claude/skills/transcribe-audio/transcription.py <caminho-do-audio> [idioma]")
        sys.exit(1)

    audio_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "pt"

    try:
        resultado = transcribe(audio_path, language)
        sys.stdout.buffer.write(
            json.dumps(resultado, ensure_ascii=False, indent=2).encode("utf-8")
        )
    except (FileNotFoundError, PermissionError, RuntimeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
