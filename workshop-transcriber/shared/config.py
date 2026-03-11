import os
from dotenv import load_dotenv

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not ASSEMBLYAI_API_KEY:
    raise EnvironmentError(
        "❌ ASSEMBLYAI_API_KEY não encontrada. "
        "Configure o arquivo .env antes de continuar."
    )

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
