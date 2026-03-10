"""
Script responsável por formatar a transcrição JSON em documento Markdown estruturado.

Uso via CLI:
    python .claude/skills/format-transcript/formatter.py <caminho-do-json>

Exemplo:
    python .claude/skills/format-transcript/formatter.py output/workshop.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _ms_para_timestamp(ms: int) -> str:
    """Converte milissegundos em string legível no formato MM:SS ou HH:MM:SS."""
    segundos = ms // 1000
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60

    if horas > 0:
        return f"{horas:02d}:{minutos:02d}:{segs:02d}"
    return f"{minutos:02d}:{segs:02d}"


def _duracao_legivel(segundos: float) -> str:
    """Converte duração em segundos para texto legível, ex: '1h 23min 45s'."""
    total = int(segundos)
    horas = total // 3600
    minutos = (total % 3600) // 60
    segs = total % 60

    partes = []
    if horas:
        partes.append(f"{horas}h")
    if minutos:
        partes.append(f"{minutos}min")
    if segs or not partes:
        partes.append(f"{segs}s")

    return " ".join(partes)


def _contar_locutores(utterances: list[dict]) -> int:
    """Retorna o número de locutores únicos."""
    return len({u.get("speaker") for u in utterances if u.get("speaker")})


def _montar_markdown(dados: dict, nome_base: str) -> str:
    """Monta o conteúdo completo do documento Markdown."""
    texto_corrido: str = dados.get("text", "")
    utterances: list[dict] = dados.get("utterances", [])
    duracao: float = dados.get("duration", 0)

    data_processamento = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    linhas = []

    # Cabeçalho e metadados
    linhas.append(f"# {nome_base}\n")
    linhas.append("## Metadados\n")
    linhas.append(f"- **Processado em:** {data_processamento}")
    linhas.append(f"- **Duração total:** {_duracao_legivel(duracao)}")
    linhas.append(f"- **Locutores identificados:** {_contar_locutores(utterances)}")
    linhas.append("")

    # Transcrição por locutor com timestamps
    if utterances:
        linhas.append("## Transcrição por Locutor\n")
        for u in utterances:
            timestamp = _ms_para_timestamp(u.get("start", 0))
            speaker = u.get("speaker", "?")
            texto = u.get("text", "").strip()
            linhas.append(f"**[{timestamp}] Speaker {speaker}**")
            linhas.append(f"{texto}\n")

    # Transcrição corrida
    if texto_corrido:
        linhas.append("## Transcrição Completa\n")
        linhas.append(texto_corrido)
        linhas.append("")

    return "\n".join(linhas)


def format_transcript(json_path: str) -> str:
    """
    Lê o JSON de transcrição e gera um arquivo Markdown em output/.

    Args:
        json_path: Caminho para o arquivo JSON gerado por transcription.py.

    Returns:
        Caminho do arquivo Markdown gerado.
    """
    caminho_json = Path(json_path)

    if not caminho_json.is_file():
        raise FileNotFoundError(
            f"❌ Arquivo JSON não encontrado: {json_path}"
        )

    if caminho_json.suffix.lower() != ".json":
        raise ValueError(
            f"❌ O arquivo informado não é um JSON: {json_path}"
        )

    # Lê o JSON
    try:
        dados = json.loads(caminho_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ JSON inválido: {e}") from e

    # Define o arquivo de saída em output/ com o mesmo nome base
    pasta_output = Path("output")
    pasta_output.mkdir(exist_ok=True)

    nome_base = caminho_json.stem
    caminho_md = pasta_output / f"{nome_base}.md"

    # Gera e salva o Markdown
    conteudo = _montar_markdown(dados, nome_base)
    caminho_md.write_text(conteudo, encoding="utf-8")

    return str(caminho_md)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python .claude/skills/format-transcript/formatter.py <caminho-do-json>")
        sys.exit(1)

    json_path = sys.argv[1]

    try:
        caminho_gerado = format_transcript(json_path)
        print(caminho_gerado)
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
