"""
Script responsável por baixar áudio de links do YouTube ou Google Drive.

Uso via CLI:
    python .claude/skills/download-audio/downloader.py <url>
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


# Diretório temporário para salvar os áudios baixados (cross-platform)
AUDIO_DIR = str(Path(tempfile.gettempdir()) / "workshop_audio")

# Usa o yt-dlp do mesmo ambiente Python em execução
YT_DLP = str(Path(sys.executable).parent / "yt-dlp")

# Localiza o ffmpeg: primeiro no PATH, depois no local padrão do winget
def _encontrar_ffmpeg() -> str | None:
    """Retorna o caminho do ffmpeg se encontrado, ou None."""
    import shutil
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    # Local padrão do winget no Windows
    winget_ffmpeg = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    for ffmpeg_bin in winget_ffmpeg.glob("Gyan.FFmpeg_*/ffmpeg-*/bin/ffmpeg.exe"):
        return str(ffmpeg_bin)
    return None


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

    comando = [YT_DLP, "--extract-audio", "--audio-format", "mp3",
               "--output", output_template, "--print", "after_move:filepath"]

    ffmpeg = _encontrar_ffmpeg()
    if ffmpeg:
        comando += ["--ffmpeg-location", str(Path(ffmpeg).parent)]

    comando.append(url)

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

    raise ValueError("❌ URL não reconhecida. Use um link do YouTube ou Google Drive.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python .claude/skills/download-audio/downloader.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    try:
        caminho = download_audio(url)
        print(caminho)
    except (RuntimeError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
