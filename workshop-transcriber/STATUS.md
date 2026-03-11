# Status do Projeto — Banco de Conteúdo Instagram Felipe

## O que foi feito

### ✅ Vídeos (34/34 concluídos)
- Baixados com `yt-dlp` (suporta Instagram sem login)
- Transcritos com AssemblyAI (diarização em português)
- Formatados em Markdown
- Consolidados em `knowledge/base-conhecimento.md`

Arquivos em `output/`: `insta_<post_id>.json` e `insta_<post_id>.md`

Script usado: `processar_instagram.py`

---

### 🔄 Carrosséis (1/31 concluído)
- Processo usa **Playwright** (Python) para navegar nos posts
- Extrai imagens de cada slide via `?img_index=N`
- OCR dos slides com **GPT-4o Vision** (OpenAI)
- Salva em `output/carrossel_<post_id>.json` e `.md`
- Ao final consolida em `knowledge/carrosséis.md`

**Concluído:** `DIMKzJ_xBui` (4 slides)
**Pendentes:** 30 restantes da lista abaixo

Script: `processar_carrosseis.py`

---

## Próximo passo: adicionar login ao processo

O processo atual roda **sem login** mas é lento (navega slide por slide).
Com login ficaria mais estável e rápido.

**Para adicionar login:**
1. Modificar `processar_carrosseis.py` para rodar em modo **headed** (com janela visível)
2. Usuária loga no Instagram uma vez
3. Salva sessão (cookies) em arquivo
4. Script reutiliza a sessão para todos os carrosséis

---

## Lista de carrosséis pendentes

```
DH8uSo0xkjM   → https://www.instagram.com/p/DH8uSo0xkjM/
DJ67LpYx-gW   → https://www.instagram.com/p/DJ67LpYx-gW/
DKvAS0Pugfc   → https://www.instagram.com/p/DKvAS0Pugfc/
DKzc1iaORkz   → https://www.instagram.com/p/DKzc1iaORkz/
DLBEtCcuuP9   → https://www.instagram.com/p/DLBEtCcuuP9/   (Prova Social)
DLYUI7fuPIJ   → https://www.instagram.com/p/DLYUI7fuPIJ/
DL0fFNNOZIV   → https://www.instagram.com/p/DL0fFNNOZIV/   (Prova social)
DL-JYTTufNz   → https://www.instagram.com/p/DL-JYTTufNz/
DMEF0k1unPT   → https://www.instagram.com/p/DMEF0k1unPT/
DMJF5IvuR9G   → https://www.instagram.com/p/DMJF5IvuR9G/
DMbSE0sOIwQ   → https://www.instagram.com/p/DMbSE0sOIwQ/
DMgdQNbOM6t   → https://www.instagram.com/p/DMgdQNbOM6t/
DMqrG3sOxuV   → https://www.instagram.com/p/DMqrG3sOxuV/
DM6JHzCuBZk   → https://www.instagram.com/p/DM6JHzCuBZk/
DNOuRNwu72m   → https://www.instagram.com/p/DNOuRNwu72m/
DNTqKliOk9_   → https://www.instagram.com/p/DNTqKliOk9_/
DNwFgz-3HsM   → https://www.instagram.com/p/DNwFgz-3HsM/
DN8M6kCCMoX   → https://www.instagram.com/p/DN8M6kCCMoX/
DORVXLXjujv   → https://www.instagram.com/p/DORVXLXjujv/
DOetFVoDuP-   → https://www.instagram.com/p/DOetFVoDuP-/
DOwrgwlDjk7   → https://www.instagram.com/p/DOwrgwlDjk7/
DPCyHobDodA   → https://www.instagram.com/p/DPCyHobDodA/
DPZomDWjjzU   → https://www.instagram.com/p/DPZomDWjjzU/
DQU_QuajnCo   → https://www.instagram.com/p/DQU_QuajnCo/
DQ5MVK9jpdL   → https://www.instagram.com/p/DQ5MVK9jpdL/
DRdGnAlDn63   → https://www.instagram.com/p/DRdGnAlDn63/
DSnueQikiy7   → https://www.instagram.com/p/DSnueQikiy7/   (Workshop)
DTgbLSDjqc6   → https://www.instagram.com/p/DTgbLSDjqc6/   (Prova Social)
DTyl_bwDtbW   → https://www.instagram.com/p/DTyl_bwDtbW/   (Prova Social)
DUy6HuxDtT5   → https://www.instagram.com/p/DUy6HuxDtT5/
```

---

## Estrutura de arquivos

```
workshop-transcriber/
  processar_instagram.py       ← script de vídeos (concluído)
  processar_carrosseis.py      ← script de carrosséis (em andamento)
  output/
    insta_*.json/.md           ← transcrições de vídeos (34 arquivos)
    carrossel_*.json/.md       ← copys de carrosséis (1 concluído)
  knowledge/
    base-conhecimento.md       ← vídeos + workshops + PDFs consolidados
    carrosséis.md              ← será gerado ao fim do processamento
  shared/config.py             ← ASSEMBLYAI_API_KEY + OPENAI_API_KEY
  .env                         ← chaves de API
```

## Dependências instaladas

- `yt-dlp` — download de vídeos
- `assemblyai` / `httpx` — transcrição
- `openai` — GPT-4o Vision (OCR dos carrosséis)
- `playwright` + Chromium — navegação nos carrosséis
- `pymupdf` — leitura de PDFs
