"""
Processa carrosséis do Instagram: extrai texto de cada slide via GPT-4o Vision
e salva os resultados em output/ e knowledge/carrosséis.md

Uso:
    .venv/Scripts/python processar_carrosseis.py
"""

import base64
import json
import sys
import time
from pathlib import Path

import httpx
from openai import OpenAI
from playwright.sync_api import sync_playwright

sys.path.insert(0, ".")
from shared.config import OPENAI_API_KEY

OUTPUT_DIR = Path("output")
KNOWLEDGE_DIR = Path("knowledge")
KNOWLEDGE_FILE = KNOWLEDGE_DIR / "carrosséis.md"

CARROSSEIS = [
    ("DH8uSo0xkjM", "https://www.instagram.com/p/DH8uSo0xkjM/"),
    ("DIMKzJ_xBui", "https://www.instagram.com/p/DIMKzJ_xBui/"),
    ("DJ67LpYx-gW", "https://www.instagram.com/p/DJ67LpYx-gW/"),
    ("DKvAS0Pugfc", "https://www.instagram.com/p/DKvAS0Pugfc/"),
    ("DKzc1iaORkz", "https://www.instagram.com/p/DKzc1iaORkz/"),
    ("DLBEtCcuuP9", "https://www.instagram.com/p/DLBEtCcuuP9/"),   # Prova Social
    ("DLYUI7fuPIJ", "https://www.instagram.com/p/DLYUI7fuPIJ/"),
    ("DL0fFNNOZIV", "https://www.instagram.com/p/DL0fFNNOZIV/"),   # Prova social
    ("DL-JYTTufNz", "https://www.instagram.com/p/DL-JYTTufNz/"),
    ("DMEF0k1unPT", "https://www.instagram.com/p/DMEF0k1unPT/"),
    ("DMJF5IvuR9G", "https://www.instagram.com/p/DMJF5IvuR9G/"),
    ("DMbSE0sOIwQ", "https://www.instagram.com/p/DMbSE0sOIwQ/"),
    ("DMgdQNbOM6t", "https://www.instagram.com/p/DMgdQNbOM6t/"),
    ("DMqrG3sOxuV", "https://www.instagram.com/p/DMqrG3sOxuV/"),
    ("DM6JHzCuBZk", "https://www.instagram.com/p/DM6JHzCuBZk/"),
    ("DNOuRNwu72m", "https://www.instagram.com/p/DNOuRNwu72m/"),
    ("DNTqKliOk9_", "https://www.instagram.com/p/DNTqKliOk9_/"),
    ("DNwFgz-3HsM", "https://www.instagram.com/p/DNwFgz-3HsM/"),
    ("DN8M6kCCMoX", "https://www.instagram.com/p/DN8M6kCCMoX/"),
    ("DORVXLXjujv", "https://www.instagram.com/p/DORVXLXjujv/"),
    ("DOetFVoDuP-", "https://www.instagram.com/p/DOetFVoDuP-/"),
    ("DOwrgwlDjk7", "https://www.instagram.com/p/DOwrgwlDjk7/"),
    ("DPCyHobDodA", "https://www.instagram.com/p/DPCyHobDodA/"),
    ("DPZomDWjjzU", "https://www.instagram.com/p/DPZomDWjjzU/"),
    ("DQU_QuajnCo", "https://www.instagram.com/p/DQU_QuajnCo/"),
    ("DQ5MVK9jpdL", "https://www.instagram.com/p/DQ5MVK9jpdL/"),
    ("DRdGnAlDn63", "https://www.instagram.com/p/DRdGnAlDn63/"),
    ("DSnueQikiy7", "https://www.instagram.com/p/DSnueQikiy7/"),   # Workshop
    ("DTgbLSDjqc6", "https://www.instagram.com/p/DTgbLSDjqc6/"),   # Prova Social
    ("DTyl_bwDtbW", "https://www.instagram.com/p/DTyl_bwDtbW/"),   # Prova Social
    ("DUy6HuxDtT5", "https://www.instagram.com/p/DUy6HuxDtT5/"),
]


def ja_processado(post_id: str) -> bool:
    return (OUTPUT_DIR / f"carrossel_{post_id}.json").exists()


def _get_slide_imgs(page) -> list[str]:
    """Retorna todas as URLs de imagens do carrossel visíveis na página."""
    return page.evaluate("""() => {
        const main = document.querySelector('main');
        if (!main) return [];
        return Array.from(main.querySelectorAll('img'))
            .filter(img =>
                img.src.includes('fbcdn') &&
                !img.src.includes('44x44') &&
                !img.src.includes('150x150') &&
                img.alt && img.alt.startsWith('Photo by')
            )
            .map(img => img.src);
    }""")


def _get_legenda(page) -> str:
    """Extrai a legenda do post."""
    return page.evaluate("""() => {
        const main = document.querySelector('main');
        if (!main) return '';
        const h1 = main.querySelector('h1');
        return h1 ? h1.innerText.trim() : '';
    }""")


def _imagem_id(url: str) -> str:
    """Extrai o nome do arquivo da URL para identificar imagens únicas."""
    # Ex: .../486749464_18473483665070289_n.jpg?... → 486749464_18473483665070289_n.jpg
    path = url.split("?")[0]
    return path.split("/")[-1]


def extrair_slides_e_legenda(page, base_url: str) -> tuple[list[str], str]:
    """Navega em grupos de slides via ?img_index=N e coleta todas as imagens únicas."""
    url_limpa = base_url.split('?')[0].rstrip('/')

    imagens = []
    ids_vistos = set()
    legenda = ""
    idx = 1

    while idx <= 30:  # máximo 30 slides
        url_slide = f"{url_limpa}/?img_index={idx}"
        page.goto(url_slide, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        if idx == 1:
            legenda = _get_legenda(page)

        novas = _get_slide_imgs(page)

        novas_unicas = []
        for url_img in novas:
            key = _imagem_id(url_img)
            if key not in ids_vistos:
                ids_vistos.add(key)
                novas_unicas.append(url_img)

        if not novas_unicas:
            break  # nenhuma imagem nova = fim do carrossel

        imagens.extend(novas_unicas)
        idx += len(novas)  # avança pelo número de slides visíveis

    return imagens, legenda


def ocr_slide(url_img: str, client: OpenAI) -> str:
    """Baixa imagem e extrai texto com GPT-4o Vision."""
    r = httpx.get(url_img, headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True, timeout=30)
    img_b64 = base64.b64encode(r.content).decode()

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": (
                "Extraia todo o texto visível nesta imagem, na ordem de leitura. "
                "Preserve a estrutura (título, subtítulo, corpo, CTA). "
                "Responda apenas com o texto extraído, sem comentários."
            )}
        ]}],
        max_tokens=1000
    )
    return resp.choices[0].message.content.strip()


def salvar_json(post_id: str, legenda: str, slides: list[dict]) -> Path:
    dados = {"post_id": post_id, "tipo": "carrossel", "legenda": legenda, "slides": slides}
    caminho = OUTPUT_DIR / f"carrossel_{post_id}.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def salvar_md(post_id: str, legenda: str, slides: list[dict]) -> Path:
    linhas = [f"# Carrossel {post_id}\n", f"**Legenda:** {legenda}\n\n"]
    for s in slides:
        linhas.append(f"## Slide {s['numero']}\n{s['texto']}\n\n")
    caminho = OUTPUT_DIR / f"carrossel_{post_id}.md"
    caminho.write_text("".join(linhas), encoding="utf-8")
    return caminho


def consolidar_knowledge():
    """Consolida todos os MDs de carrosséis em knowledge/carrosséis.md"""
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    mds = sorted(OUTPUT_DIR.glob("carrossel_*.md"))
    linhas = ["# Base de Conhecimento — Carrosséis do Instagram\n\n"]
    for md in mds:
        linhas.append(md.read_text(encoding="utf-8"))
        linhas.append("\n---\n\n")
    KNOWLEDGE_FILE.write_text("".join(linhas), encoding="utf-8")
    print(f"\nKnowledge consolidado: {KNOWLEDGE_FILE} ({len(mds)} carrosséis)")


def main():
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não encontrada no .env", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=OPENAI_API_KEY)
    total = len(CARROSSEIS)
    erros = []

    print(f"\n{'='*50}")
    print(f"Processando {total} carrosséis do Instagram")
    print(f"{'='*50}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for i, (post_id, url) in enumerate(CARROSSEIS, 1):
            print(f"[{i}/{total}] {post_id}")

            if ja_processado(post_id):
                print(f"  Já processado, pulando.")
                continue

            try:
                print(f"  Navegando e extraindo slides...")
                imagens, legenda = extrair_slides_e_legenda(page, url)

                if not imagens:
                    print(f"  Nenhuma imagem encontrada, pulando.")
                    erros.append(post_id)
                    continue

                print(f"  {len(imagens)} slide(s). Extraindo texto com GPT-4o...")
                slides = []
                for j, url_img in enumerate(imagens, 1):
                    texto = ocr_slide(url_img, client)
                    slides.append({"numero": j, "texto": texto})
                    print(f"    Slide {j}: {texto[:60]}...")

                salvar_json(post_id, legenda, slides)
                salvar_md(post_id, legenda, slides)
                print(f"  Salvo: carrossel_{post_id}.json/.md")

            except Exception as e:
                print(f"  ERRO: {e}", file=sys.stderr)
                erros.append(post_id)

            time.sleep(2)

        browser.close()

    consolidar_knowledge()

    print(f"\n{'='*50}")
    print(f"Concluído: {total - len(erros)} processados, {len(erros)} erros")
    if erros:
        print(f"Erros: {', '.join(erros)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
