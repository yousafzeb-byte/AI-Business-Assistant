import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _require_env(key: str) -> str:
    """Return env var or abort if missing (production safety)."""
    value = os.getenv(key)
    if not value:
        print(f"FATAL: required environment variable {key} is not set", file=sys.stderr)
        sys.exit(1)
    return value


class Config:
    SECRET_KEY = _require_env("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _require_env("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "max_overflow": 20,
    }

    JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB upload limit
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
