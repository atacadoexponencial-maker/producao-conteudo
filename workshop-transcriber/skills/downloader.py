"""
Skill responsável por baixar áudio de links do YouTube ou Google Drive.
"""

import os
import subprocess
from pathlib import Path


# Diretório temporário para salvar os áudios baixados
AUDIO_DIR = "/tmp/workshop_audio"


def _detectar_origem(url: str) -> str:
    """Detecta se a URL é do YouTube ou Google Drive."""
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "drive.google.com" in url:
        return "google_drive"
    return "desconhecido"


def _garantir_diretorio() -> None:
    """Cria o diretório de áudio temporário se não existir."""
    Path(AUDIO_DIR).mkdir(parents=True, exist_ok=True)


def _baixar_youtube(url: str) -> str:
    """Baixa o áudio de um vídeo do YouTube usando yt-dlp."""
    _garantir_diretorio()

    # Template de saída: usa o título do vídeo como nome do arquivo
    output_template = os.path.join(AUDIO_DIR, "%(title)s.%(ext)s")

    comando = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--output", output_template,
        "--print", "after_move:filepath",
        url,
    ]

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            check=True,
        )
        # A última linha impressa é o caminho final do arquivo
        caminho = resultado.stdout.strip().splitlines()[-1]
        return caminho
    except subprocess.CalledProcessError as e:
        detalhe = e.stderr.strip() or e.stdout.strip()
        raise RuntimeError(f"❌ Erro ao baixar do YouTube: {detalhe}") from e


def _baixar_google_drive(url: str) -> str:
    """Baixa um arquivo do Google Drive usando gdown."""
    import gdown  # importado aqui para evitar erro caso não esteja instalado

    _garantir_diretorio()

    try:
        caminho = gdown.download(url, output=AUDIO_DIR + "/", quiet=False, fuzzy=True)
        if caminho is None:
            raise RuntimeError("gdown retornou None — verifique as permissões do arquivo.")
        return os.path.abspath(caminho)
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao baixar do Google Drive: {e}") from e


def download_audio(source: str) -> str:
    """
    Baixa o áudio de um link do YouTube ou Google Drive.

    Parâmetros:
        source: URL do YouTube ou Google Drive.

    Retorna:
        Caminho completo do arquivo de áudio baixado.

    Lança:
        RuntimeError com mensagem amigável em caso de falha.
    """
    origem = _detectar_origem(source)

    if origem == "youtube":
        return _baixar_youtube(source)

    if origem == "google_drive":
        return _baixar_google_drive(source)

    return "❌ URL não reconhecida. Use um link do YouTube ou Google Drive."
