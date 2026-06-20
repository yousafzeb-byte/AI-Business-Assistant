import os
import re
import sys
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load .env from project root (one level above backend/)
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)


def _require_env(key: str) -> str:
    """Return env var or abort if missing (production safety)."""
    value = os.getenv(key)
    if not value:
        print(f"FATAL: required environment variable {key} is not set", file=sys.stderr)
        sys.exit(1)
    return value


def _build_cors_origins(frontend_url: str) -> list[object]:
    """Build allowed CORS origins with flexible localhost support for local dev."""
    origins = [frontend_url]
    extra_origins = os.getenv("CORS_ORIGINS", "")
    if extra_origins:
        origins.extend(origin.strip() for origin in extra_origins.split(",") if origin.strip())

    parsed = urlparse(frontend_url)
    if parsed.hostname in {"localhost", "127.0.0.1"}:
        origins.extend([
            re.compile(r"http://localhost:\d+"),
            re.compile(r"http://127\.0\.0\.1:\d+"),
        ])

    deduped_origins: list[object] = []
    seen_string_origins: set[str] = set()
    for origin in origins:
        if isinstance(origin, str):
            if origin in seen_string_origins:
                continue
            seen_string_origins.add(origin)
        deduped_origins.append(origin)

    return deduped_origins


class Config:
    SECRET_KEY = _require_env("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _require_env("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pool options only for non-SQLite databases
    _db_url = _require_env("DATABASE_URL")
    if not _db_url.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 10,
            "pool_recycle": 300,
            "pool_pre_ping": True,
            "max_overflow": 20,
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}

    JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS = _build_cors_origins(FRONTEND_URL)

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB upload limit
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

    # Email / SMTP — optional, required for password-reset emails
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "noreply@example.com")
