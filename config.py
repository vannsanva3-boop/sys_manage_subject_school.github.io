"""Local application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-development-secret")
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "database" / "attendance.db"))
