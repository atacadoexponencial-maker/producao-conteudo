# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git
- Nunca fazer commits, push ou criar branches — a usuária cuida de tudo isso.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in ASSEMBLYAI_API_KEY in .env
```

## Running Skills

Each skill is a standalone CLI script called via the `.venv` Python:

```bash
.venv/Scripts/python .claude/skills/download-audio/downloader.py <url>
.venv/Scripts/python .claude/skills/transcribe-audio/transcription.py <audio_file> [language]
.venv/Scripts/python .claude/skills/format-transcript/formatter.py <json_file>
.venv/Scripts/python .claude/skills/build-knowledge-base/builder.py
```

Language defaults to `pt`. Outputs go to `output/`.

## Architecture

Three-stage pipeline: **Download → Transcribe → Format**

```
.claude/
  skills/
    download-audio/downloader.py              # yt-dlp (YouTube) or gdown (Google Drive)
    transcribe-audio/transcription.py         # AssemblyAI REST API with speaker diarization
    format-transcript/formatter.py            # JSON → Markdown with timestamps
    build-knowledge-base/builder.py           # Consolidates transcriptions + PDFs into knowledge base
  agents/
    workshop-processor.md                     # Orchestrates full pipeline autonomously
shared/config.py                              # Loads/validates ASSEMBLYAI_API_KEY from .env
input/                                        # PDFs and documents for the knowledge base
output/                                       # Generated JSON and Markdown files
knowledge/base-conhecimento.md                # Consolidated knowledge base
```

Each skill follows the same CLI pattern: args via `sys.argv`, data output to stdout, errors to stderr, `sys.exit(1)` on failure.

The `workshop-processor` agent is the preferred entry point for end-to-end processing — it detects which steps are already done and runs only the missing ones.

## Data Flow

1. `downloader.py` saves audio to `tempfile.gettempdir()` and prints the file path
2. `transcription.py` uploads to AssemblyAI, polls until complete, saves `output/<name>.json`
3. `formatter.py` reads the JSON and writes `output/<name>.md` with speaker-labeled utterances and timestamps
4. `builder.py` reads all `.md` from `output/` and `.pdf` from `input/`, writes `knowledge/base-conhecimento.md`

## Key Dependencies

- `yt-dlp` — YouTube download (requires ffmpeg; auto-detected from PATH or winget default on Windows)
- `gdown` — Google Drive download
- `assemblyai` (package) + direct REST calls via `httpx` for transcription
- `python-dotenv` — env config
- `pymupdf` — PDF text extraction for knowledge base builder
