import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
ENV_EXAMPLE = BASE_DIR / ".env.example"

FAST_MODEL = os.getenv("MODEL_FAST", "").strip()
MID_MODEL = os.getenv("MODEL_MID", "").strip()
STRONG_MODEL = os.getenv("MODEL_STRONG", "").strip()

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY", "").strip()
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

logger = logging.getLogger(__name__)


def _check_model(name: str) -> str:
    if name:
        return name
    logger.warning(f"Model {name} not configured, using default placeholder")
    return "nemotron-nano"


FAST_MODEL = _check_model(FAST_MODEL)
MID_MODEL = _check_model(MID_MODEL)
STRONG_MODEL = _check_model(STRONG_MODEL)


def validate_config() -> bool:
    missing = []
    if not NEBIUS_API_KEY:
        missing.append("NEBIUS_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if not FAST_MODEL:
        missing.append("MODEL_FAST")
    if not MID_MODEL:
        missing.append("MODEL_MID")
    if not STRONG_MODEL:
        missing.append("MODEL_STRONG")
    if missing:
        logger.error(f"Missing env vars: {missing}")
        return False
    return True


AVAILABLE_MODELS = {"fast": FAST_MODEL, "mid": MID_MODEL, "strong": STRONG_MODEL}


def list_models() -> dict:
    return {"fast": FAST_MODEL, "mid": MID_MODEL, "strong": STRONG_MODEL}