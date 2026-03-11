"""
Constrói a base de conhecimento consolidando transcrições (.md) e documentos (.pdf).
Saída: knowledge/base-conhecimento.md
"""

import sys
import os
from pathlib import Path
import pymupdf  # PyMuPDF

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = ROOT / "output"
INPUT_DIR = ROOT / "input"
KNOWLEDGE_DIR = ROOT / "knowledge"
BASE_FILE = KNOWLEDGE_DIR / "base-conhecimento.md"


def extract_pdf(path: Path) -> str:
    doc = pymupdf.open(str(path))
    return "\n".join(page.get_text() for page in doc)


def read_md(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build():
    KNOWLEDGE_DIR.mkdir(exist_ok=True)

    sections = []

    # Transcrições de workshops
    md_files = sorted(OUTPUT_DIR.glob("*.md"))
    if md_files:
        sections.append("# Transcrições de Workshops\n")
        for f in md_files:
            print(f"  → Lendo transcrição: {f.name}", file=sys.stderr)
            sections.append(f"## {f.stem}\n")
            sections.append(read_md(f))
            sections.append("\n---\n")

    # Documentos PDF
    pdf_files = sorted(INPUT_DIR.glob("*.pdf"))
    if pdf_files:
        sections.append("# Documentos de Referência\n")
        for f in pdf_files:
            print(f"  → Lendo PDF: {f.name}", file=sys.stderr)
            sections.append(f"## {f.stem}\n")
            sections.append(extract_pdf(f))
            sections.append("\n---\n")

    if not sections:
        print("Nenhum arquivo encontrado em output/ ou input/", file=sys.stderr)
        sys.exit(1)

    content = "\n".join(sections)
    BASE_FILE.write_text(content, encoding="utf-8")
    print(str(BASE_FILE))


if __name__ == "__main__":
    build()
