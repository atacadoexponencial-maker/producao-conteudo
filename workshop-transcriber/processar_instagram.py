"""
Processamento em lote dos vídeos do Instagram do Felipe.
Baixa o áudio e transcreve cada post, pulando os que já foram processados.

Uso:
    .venv/Scripts/python processar_instagram.py
"""

import subprocess
import sys
import time
from pathlib import Path

PYTHON = str(Path(sys.executable))
DOWNLOADER = ".claude/skills/download-audio/downloader.py"
TRANSCRIBER = ".claude/skills/transcribe-audio/transcription.py"
OUTPUT_DIR = Path("output")

VIDEOS = [
    ("DC690moROTl", "https://www.instagram.com/p/DC690moROTl/"),
    ("DDNt0ckxcBh", "https://www.instagram.com/p/DDNt0ckxcBh/"),
    ("DFL_Hd_xuuV", "https://www.instagram.com/p/DFL_Hd_xuuV/"),
    ("DFdmEmlxu1D", "https://www.instagram.com/p/DFdmEmlxu1D/"),
    ("DGgHQibx9jv", "https://www.instagram.com/p/DGgHQibx9jv/"),
    ("DHUh-G4xPV0", "https://www.instagram.com/p/DHUh-G4xPV0/"),
    ("DHb-zT4xOhG", "https://www.instagram.com/p/DHb-zT4xOhG/"),
    ("DIjwH4GxWEt", "https://www.instagram.com/p/DIjwH4GxWEt/"),   # Depoimento
    ("DKci60FxhJZ", "https://www.instagram.com/p/DKci60FxhJZ/"),   # Depoimento
    ("DK8BEKIOSQt", "https://www.instagram.com/p/DK8BEKIOSQt/"),
    ("DLgFEIwuFY2", "https://www.instagram.com/p/DLgFEIwuFY2/"),   # Campeão
    ("DLm2L3_OUoq", "https://www.instagram.com/p/DLm2L3_OUoq/"),
    ("DL5IIZmOMzW", "https://www.instagram.com/p/DL5IIZmOMzW/"),
    ("DMYrAMAu5um", "https://www.instagram.com/p/DMYrAMAu5um/"),
    ("DMys36YRWMy", "https://www.instagram.com/p/DMys36YRWMy/"),
    ("DM_aVEBuTN3", "https://www.instagram.com/p/DM_aVEBuTN3/"),
    ("DNEXdBLOYZx", "https://www.instagram.com/p/DNEXdBLOYZx/"),
    ("DNeOO7-uNug", "https://www.instagram.com/p/DNeOO7-uNug/"),
    ("DNouWegO-7A", "https://www.instagram.com/p/DNouWegO-7A/"),
    ("DOXCzS1jlPw", "https://www.instagram.com/p/DOXCzS1jlPw/"),   # Depoimento
    ("DOZeEV0juvf", "https://www.instagram.com/p/DOZeEV0juvf/"),
    ("DOrqAfAjvrE", "https://www.instagram.com/p/DOrqAfAjvrE/"),
    ("DPHlihkjtw9", "https://www.instagram.com/p/DPHlihkjtw9/"),
    ("DQDMVHqDhBE", "https://www.instagram.com/p/DQDMVHqDhBE/"),
    ("DQaXCmzjj2q", "https://www.instagram.com/p/DQaXCmzjj2q/"),
    ("DQ7uE-ADo0d", "https://www.instagram.com/p/DQ7uE-ADo0d/"),
    ("DRX1f6Jjtq5", "https://www.instagram.com/p/DRX1f6Jjtq5/"),
    ("DRfocnsDv5e", "https://www.instagram.com/p/DRfocnsDv5e/"),   # Workshop planejamento atacado
    ("DRiVvmAjlAH", "https://www.instagram.com/p/DRiVvmAjlAH/"),
    ("DRpu5Itjg34", "https://www.instagram.com/p/DRpu5Itjg34/"),
    ("DTdv7BRknBZ", "https://www.instagram.com/p/DTdv7BRknBZ/"),
    ("DUgv6PkEjQR", "https://www.instagram.com/p/DUgv6PkEjQR/"),   # Workshop planejamento atacado
    ("DUqofAYjpm4", "https://www.instagram.com/p/DUqofAYjpm4/"),
    ("DVeOQJ3jo2o", "https://www.instagram.com/p/DVeOQJ3jo2o/"),
]


def ja_processado(post_id: str) -> bool:
    """Verifica se o JSON de transcrição já existe."""
    return any(OUTPUT_DIR.glob(f"*{post_id}*.json"))


def baixar(url: str, post_id: str) -> str | None:
    """Baixa o áudio com nome único baseado no post_id."""
    import tempfile
    audio_dir = Path(tempfile.gettempdir()) / "workshop_audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    destino = str(audio_dir / f"{post_id}.mp3")

    import shutil
    yt_dlp = str(Path(sys.executable).parent / "yt-dlp")

    # Detecta ffmpeg
    ffmpeg_cmd = shutil.which("ffmpeg")
    from pathlib import Path as P
    if not ffmpeg_cmd:
        winget = P.home() / "AppData/Local/Microsoft/WinGet/Packages"
        for p in winget.glob("Gyan.FFmpeg_*/ffmpeg-*/bin/ffmpeg.exe"):
            ffmpeg_cmd = str(p)
            break

    cmd = [yt_dlp, "--extract-audio", "--audio-format", "mp3",
           "--output", destino, "--force-overwrites"]
    if ffmpeg_cmd:
        cmd += ["--ffmpeg-location", str(Path(ffmpeg_cmd).parent)]
    cmd.append(url)

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        print(f"  ERRO download: {resultado.stderr.strip()}", file=sys.stderr)
        return None
    return destino


def transcrever(audio_path: str, post_id: str) -> bool:
    """Transcreve o áudio e salva o JSON com o post_id como nome."""
    resultado = subprocess.run(
        [PYTHON, TRANSCRIBER, audio_path, "pt"],
        capture_output=True, text=True
    )
    if resultado.returncode != 0:
        print(f"  ERRO transcrição: {resultado.stderr.strip()}", file=sys.stderr)
        return False

    destino = OUTPUT_DIR / f"insta_{post_id}.json"
    destino.write_text(resultado.stdout, encoding="utf-8")
    print(f"  Salvo: {destino.name}")
    return True


def main():
    total = len(VIDEOS)
    pulados = 0
    erros = []

    print(f"\n{'='*50}")
    print(f"Processando {total} vídeos do Instagram")
    print(f"{'='*50}\n")

    for i, (post_id, url) in enumerate(VIDEOS, 1):
        print(f"[{i}/{total}] {post_id}")

        if ja_processado(post_id):
            print(f"  Já processado, pulando.")
            pulados += 1
            continue

        print(f"  Baixando...")
        audio = baixar(url, post_id)
        if not audio:
            erros.append(post_id)
            continue

        print(f"  Transcrevendo...")
        ok = transcrever(audio, post_id)
        if not ok:
            erros.append(post_id)
            continue

        print(f"  Concluído!")
        time.sleep(2)  # Pausa entre requisições para não sobrecarregar

    print(f"\n{'='*50}")
    print(f"Concluído: {total - len(erros) - pulados} processados, {pulados} pulados, {len(erros)} erros")
    if erros:
        print(f"Erros: {', '.join(erros)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
