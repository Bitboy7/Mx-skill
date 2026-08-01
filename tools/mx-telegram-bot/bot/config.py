"""Configuración del bot (variables de entorno + .env opcional)."""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _int_list(raw: str) -> list[int]:
    return [int(part) for part in raw.split(",") if part.strip().isdigit()]


BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
DEFAULT_PLACE: str = os.getenv("BOT_DEFAULT_PLACE", "Roma Norte, Ciudad de Mexico")
DEFAULT_LAT: float | None = float(os.getenv("BOT_DEFAULT_LAT")) if os.getenv("BOT_DEFAULT_LAT") else None
DEFAULT_LON: float | None = float(os.getenv("BOT_DEFAULT_LON")) if os.getenv("BOT_DEFAULT_LON") else None
ALLOWED_USER_IDS: list[int] = _int_list(os.getenv("BOT_ALLOWED_USER_IDS", ""))

AI_API_KEY: str = os.getenv("AI_API_KEY", "")
AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")

# Ubicación compartida: redondeo de coordenadas (2 ≈ ±1 km) y vigencia.
BLUR_PRECISION: int = int(os.getenv("BOT_BLUR_PRECISION", "2"))
BLUR_APPROX_KM: float = float(os.getenv("BOT_BLUR_APPROX_KM", "1.1"))
LOCATION_MAX_AGE: int = int(os.getenv("BOT_LOCATION_MAX_AGE", "3600"))

# Persistencia opcional de user_data (ruta a un archivo pickle). Vacío = en memoria.
PERSISTENCE_FILE: str = os.getenv("BOT_PERSISTENCE_FILE", "")

MAX_REPLY_LEN: int = 4000
