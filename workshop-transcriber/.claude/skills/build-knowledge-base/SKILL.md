---
description: Constrói ou atualiza a base de conhecimento consolidando transcrições de output/ e PDFs de input/
---

Execute o script de construção da base de conhecimento:

```bash
.venv/Scripts/python .claude/skills/build-knowledge-base/builder.py
```

O script lê todos os `.md` de `output/` e `.pdf` de `input/` e consolida em `knowledge/base-conhecimento.md`.

Mostre ao usuário o caminho do arquivo gerado e confirme quantas transcrições e PDFs foram processados.
Se ocorrer erro, exiba a mensagem retornada pelo script.
