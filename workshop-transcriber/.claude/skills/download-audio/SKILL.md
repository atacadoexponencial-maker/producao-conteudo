---
description: Baixa o áudio de uma URL do YouTube ou Google Drive e salva localmente
argument-hint: "<url>"
---

Execute o script de download passando a URL fornecida:

```bash
.venv/Scripts/python .claude/skills/download-audio/downloader.py "$ARGUMENTS"
```

Mostre ao usuário o caminho do arquivo baixado.
Se ocorrer erro, exiba a mensagem retornada pelo script.
