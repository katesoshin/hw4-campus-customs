"""Configuration and shared paths for the Campus Customs backend."""
from __future__ import annotations

import os
from functools import cache
from pathlib import Path

from dotenv import load_dotenv

# backend/ -> hw4/ -> project root (where .env lives)
BACKEND_DIR = Path(__file__).resolve().parent
HW4_DIR = BACKEND_DIR.parent
PROJECT_ROOT = HW4_DIR.parent

DATA_DIR = HW4_DIR / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
PRODUCTS_DIR = DATA_DIR / "products"

# Model choice: Portkey/OpenAI. A capable 5.6/6-series model for the chat agent.
CHAT_MODEL = os.getenv("CAMPUS_CHAT_MODEL", "gpt-5.6-luna")
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"

# Auth: pbkdf2_sha256. New hashes embed their own iteration count, so they are
# self-describing. Legacy seeded hashes use the 3-part format without an iteration
# count; LEGACY_PBKDF2_ITERATIONS is the count assumed for those.
PBKDF2_ITERATIONS = int(os.getenv("CAMPUS_PBKDF2_ITERATIONS", "260000"))
LEGACY_PBKDF2_ITERATIONS = int(os.getenv("CAMPUS_LEGACY_PBKDF2_ITERATIONS", "260000"))
SECRET_KEY = os.getenv("CAMPUS_SECRET_KEY", "dev-only-campus-customs-secret-change-me")
TOKEN_TTL_HOURS = 24 * 7


@cache
def portkey_api_key() -> str:
    """Load PORTKEY_API_KEY from hw4/.env (self-contained repo); fall back to the workspace
    parent .env for local development. Never printed or logged."""
    load_dotenv(HW4_DIR / ".env")          # preferred: hw4/.env (see .env.example)
    load_dotenv(PROJECT_ROOT / ".env")     # fallback for this workspace; does not override
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError(
            "PORTKEY_API_KEY is missing. Copy hw4/.env.example to hw4/.env and set your key."
        )
    return key
