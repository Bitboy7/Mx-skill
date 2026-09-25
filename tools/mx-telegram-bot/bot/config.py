"""Configuración del bot (variables de entorno + .env opcional)."""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _int_list(raw: str) -> list[int]:
    return [int(part) for part in raw.split(",") if part.strip().isdigit()]


def _opt_float(raw: str) -> float | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    try:
        return int(raw) if raw not in (None, "") else default
    except ValueError:
        return default


BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
DEFAULT_PLACE: str = os.getenv("BOT_DEFAULT_PLACE", "Roma Norte, Ciudad de Mexico")
DEFAULT_LAT: float | None = float(os.getenv("BOT_DEFAULT_LAT")) if os.getenv("BOT_DEFAULT_LAT") else None
DEFAULT_LON: float | None = float(os.getenv("BOT_DEFAULT_LON")) if os.getenv("BOT_DEFAULT_LON") else None
ALLOWED_USER_IDS: list[int] = _int_list(os.getenv("BOT_ALLOWED_USER_IDS", ""))

AI_API_KEY: str = os.getenv("AI_API_KEY", "")
AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")
# Temperatura opcional. Vacío = no se envía (compatible con modelos que solo
# aceptan el valor por defecto, p. ej. gpt-6-luna). Ej.: AI_TEMPERATURE=0.
AI_TEMPERATURE: float | None = _opt_float(os.getenv("AI_TEMPERATURE"))

# Límite de tasa de /ask para no agotar los tokens de la API.
# Máximo de consultas por usuario en la ventana (0 = sin límite por usuario).
AI_RATE_LIMIT: int = _int_env("AI_RATE_LIMIT", 5)
# Ventana en segundos.
AI_RATE_WINDOW: int = _int_env("AI_RATE_WINDOW", 60)
# Máximo global en la ventana (0 = sin límite global).
AI_RATE_LIMIT_GLOBAL: int = _int_env("AI_RATE_LIMIT_GLOBAL", 0)

# Ubicación compartida: redondeo de coordenadas (2 ≈ ±1 km) y vigencia.
BLUR_PRECISION: int = int(os.getenv("BOT_BLUR_PRECISION", "2"))
BLUR_APPROX_KM: float = float(os.getenv("BOT_BLUR_APPROX_KM", "1.1"))
LOCATION_MAX_AGE: int = int(os.getenv("BOT_LOCATION_MAX_AGE", "3600"))

# Persistencia opcional de user_data (ruta a un archivo pickle). Vacío = en memoria.
PERSISTENCE_FILE: str = os.getenv("BOT_PERSISTENCE_FILE", "")

# Logging: nivel (DEBUG, INFO, WARNING, ERROR) y archivo opcional (vacío = solo stdout).
LOG_LEVEL: str = os.getenv("BOT_LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("BOT_LOG_FILE", "")

MAX_REPLY_LEN: int = 4000
