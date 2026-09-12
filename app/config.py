import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel (y otros entornos serverless) exponen esta variable. Allí el sistema de
# archivos es de solo lectura salvo /tmp, y cada petición puede ejecutarse en una
# instancia distinta.
EN_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))


def _normalized_database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        # Sin base de datos configurada: en serverless solo /tmp es escribible.
        destino = Path("/tmp") if EN_SERVERLESS else (BASE_DIR / "instance")
        return f"sqlite:///{destino / 'digaloconflores.db'}"
    # Render/Heroku entregan "postgres://", SQLAlchemy 2.x exige "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-not-secure")

    SQLALCHEMY_DATABASE_URI = _normalized_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # En serverless conviene no reutilizar conexiones entre invocaciones: se
    # comprueban antes de usarlas y se reciclan pronto para no agotar el límite
    # de conexiones de la base de datos.
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"pool_pre_ping": True, "pool_recycle": 280, "pool_size": 1, "max_overflow": 2}
        if not SQLALCHEMY_DATABASE_URI.startswith("sqlite")
        else {"pool_pre_ping": True}
    )

    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Cookies solo por HTTPS en producción (en local seguirían sin funcionar)
    SESSION_COOKIE_SECURE = EN_SERVERLESS or os.environ.get("FORCE_HTTPS") == "1"
    # Una sesion no dura indefinidamente: si alguien deja la cuenta abierta en
    # un equipo prestado, caduca sola. "Recordarme" usa su propia duracion.
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get("SESSION_DAYS", 7)))
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = EN_SERVERLESS or os.environ.get("FORCE_HTTPS") == "1"
    REMEMBER_COOKIE_SAMESITE = "Lax"
    # El token CSRF caduca con la sesion y no antes: asi un formulario abierto
    # un rato no falla al enviarse.
    WTF_CSRF_TIME_LIMIT = None

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "1") == "1"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@digaloconflores.com")

    SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:5000")

    # Aviso de pedidos nuevos por WhatsApp (API oficial de Meta). Si faltan,
    # simplemente no se envia el aviso; ver app/services/whatsapp.py.
    WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
    WHATSAPP_TO = os.environ.get("WHATSAPP_TO")
    WHATSAPP_TEMPLATE = os.environ.get("WHATSAPP_TEMPLATE")
    WHATSAPP_LANG = os.environ.get("WHATSAPP_LANG", "es")
    CURRENCY = os.environ.get("CURRENCY", "COP")
    TIMEZONE = os.environ.get("TIMEZONE", "America/Bogota")

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

    # Los archivos subidos se guardan en la base de datos (ver app/utils/uploads.py),
    # no en disco, para que funcionen en hosting serverless.
    MAX_CONTENT_LENGTH = 30 * 1024 * 1024  # 30 MB: cabe una foto de celular sin recortar

    # Caché de los archivos estáticos servidos por Flask (en Vercel los sirve el CDN)
    SEND_FILE_MAX_AGE_DEFAULT = 60 * 60 * 24 * 7

    # En serverless nunca se activa el depurador, aunque la variable llegue a
    # estar puesta por error: expondria trazas completas y una consola.
    DEBUG = (not EN_SERVERLESS) and os.environ.get("FLASK_DEBUG", "0") == "1"
