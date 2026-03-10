---
description: Transcreve um arquivo de áudio usando a API da AssemblyAI com diarização por locutor
argument-hint: "<caminho-do-arquivo> [idioma]"
---

Execute o script de transcrição com o arquivo informado:

```bash
.venv/Scripts/python .claude/skills/transcribe-audio/transcription.py "$ARGUMENTS"
```

O script aceita dois argumentos:
- Caminho do arquivo de áudio (obrigatório)
- Código do idioma, ex: `pt`, `en` (opcional, padrão: `pt`)

Mostre ao usuário:
1. A transcrição completa em texto corrido
2. As falas separadas por locutor (Speaker A, Speaker B…) com timestamps
3. A duração total do áudio

Se ocorrer erro, exiba a mensagem retornada pelo script.
