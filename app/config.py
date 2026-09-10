import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _normalized_database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{BASE_DIR / 'instance' / 'digaloconflores.db'}"
    # Render/Heroku entregan "postgres://", SQLAlchemy 2.x exige "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-not-secure")

    SQLALCHEMY_DATABASE_URI = _normalized_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "1") == "1"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@digaloconflores.com")

    SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:5000")
    CURRENCY = os.environ.get("CURRENCY", "COP")

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

    UPLOAD_FOLDER = str(BASE_DIR / "app" / "static" / "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB por subida

    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
