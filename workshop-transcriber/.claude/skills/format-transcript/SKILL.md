---
description: Formata uma transcrição bruta em documento estruturado com resumo, tópicos e falas por locutor
argument-hint: "<caminho-do-arquivo-json>"
---

Execute o script de formatação com o arquivo JSON da transcrição:

```bash
.venv/Scripts/python .claude/skills/format-transcript/formatter.py "$ARGUMENTS"
```

O script recebe o JSON gerado pelo script de transcrição e produz um arquivo `.md` em `output/` com:
- Título e metadados (data, duração)
- Transcrição completa formatada
- Falas separadas por locutor com timestamps legíveis
- Resumo dos principais pontos abordados

Mostre ao usuário o caminho do arquivo gerado e um preview do conteúdo.
Se ocorrer erro, exiba a mensagem retornada pelo script.
