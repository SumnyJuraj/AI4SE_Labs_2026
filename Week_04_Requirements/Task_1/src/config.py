import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 3 Different models to satisfy ANS4
EXTRACTOR_MODEL = os.getenv("EXTRACTOR_MODEL", "gpt-4o-mini")
CONSOLIDATOR_MODEL = os.getenv("CONSOLIDATOR_MODEL", "gpt-5.6-luna")
CRITIC_MODEL = os.getenv("CRITIC_MODEL", "gpt-6-luna")

MAX_FEEDBACK_ITERATIONS = int(os.getenv("MAX_FEEDBACK_ITERATIONS", "2"))
