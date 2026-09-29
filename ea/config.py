import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
SHADOW_MODE = os.getenv("SHADOW_MODE", "true").lower() == "true"
USER_ID = os.getenv("USER_ID", "user_001")
DECISION_POLICY = os.getenv("DECISION_POLICY", "llm").lower()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

GOOGLE_CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_IDS = [x.strip() for x in os.getenv("SLACK_CHANNEL_IDS", "").split(",") if x.strip()]

FUTUREAGI_ENABLED = os.getenv("FUTUREAGI_ENABLED", "false").lower() == "true"
FUTUREAGI_OBSERVE_ENABLED = os.getenv("FUTUREAGI_OBSERVE_ENABLED", "false").lower() == "true"
FUTUREAGI_PROTECT_ENABLED = os.getenv("FUTUREAGI_PROTECT_ENABLED", "false").lower() == "true"
FI_API_KEY = os.getenv("FI_API_KEY", "")
FI_SECRET_KEY = os.getenv("FI_SECRET_KEY", "")
FUTUREAGI_PROJECT = os.getenv("FUTUREAGI_PROJECT", "TGA_EXECUTIVE_ASSISTANT")
FUTUREAGI_SIMULATION_ID = os.getenv("FUTUREAGI_SIMULATION_ID", "")
FUTUREAGI_OPT_MODEL = os.getenv("FUTUREAGI_OPT_MODEL", "gpt-4o-mini")
