# Workshop Transcriber

Transcreve automaticamente gravações de workshops a partir de links do YouTube ou Google Drive, gerando um documento Markdown estruturado com transcrição por locutor e timestamps.

## Pré-requisitos

- Python 3.10+
- Conta na [AssemblyAI](https://www.assemblyai.com/) com chave de API

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Configure sua chave de API no arquivo `.env`:

```bash
cp .env.example .env
# edite .env e preencha ASSEMBLYAI_API_KEY=sua_chave
```

## Uso no Claude Code

### Skills individuais

| Skill | Comando | Descrição |
|---|---|---|
| Download | `/download-audio <url>` | Baixa o áudio de uma URL do YouTube ou Google Drive |
| Transcrição | `/transcribe-audio <arquivo> [idioma]` | Transcreve o áudio via AssemblyAI |
| Formatação | `/format-transcript <arquivo.json>` | Gera documento Markdown estruturado |

### Pipeline completo (agente)

Use o agente `workshop-processor` para processar do início ao fim:

> "Processe este workshop: https://youtube.com/..."

O agente executa as três etapas automaticamente e salva o resultado em `output/`.

## Estrutura do projeto

```
.claude/
  skills/
    download-audio/       # /download-audio
      SKILL.md
      downloader.py
    transcribe-audio/     # /transcribe-audio
      SKILL.md
      transcription.py
    format-transcript/    # /format-transcript
      SKILL.md
      formatter.py
  agents/
    workshop-processor.md # agente do pipeline completo
shared/
  config.py               # carrega variáveis de ambiente
output/                   # documentos gerados
requirements.txt
.env                      # não commitado
```

## Idiomas suportados

Qualquer idioma suportado pela AssemblyAI. Exemplos: `pt` (português), `en` (inglês), `es` (espanhol).
