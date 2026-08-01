"""Ubicación compartida del usuario para las skills de cercanía.

El usuario comparte su ubicación por Telegram (mensaje tipo Location). Se guarda
en `context.user_data` (por usuario, opcionalmente persistido a disco) y
cualquier skill de cercanía la consume vía `get(context)`.

Privacidad: las coordenadas se guardan REDONDEADAS (precisión configurable, por
defecto ~1 km) para no usar la ubicación exacta.
"""

from __future__ import annotations

import time

from . import config

KEY = "mx_location"


def blur(latitude: float, longitude: float, precision: int | None = None) -> tuple[float, float]:
    """Redondea las coordenadas para aproximarlas (≈1 km con precision=2)."""
    p = config.BLUR_PRECISION if precision is None else precision
    return round(latitude, p), round(longitude, p)


def save(context, latitude: float, longitude: float) -> dict:
    """Guarda (y aproxima) la ubicación del usuario. Devuelve el snapshot."""
    lat, lon = blur(latitude, longitude)
    snapshot = {
        "lat": lat,
        "lon": lon,
        "timestamp": time.time(),
        "approx_km": config.BLUR_APPROX_KM,
    }
    if hasattr(context, "user_data"):
        context.user_data[KEY] = snapshot
    return snapshot


def get(context) -> dict | None:
    """Devuelve la última ubicación del usuario, o None."""
    if not hasattr(context, "user_data"):
        return None
    return context.user_data.get(KEY)


def is_fresh(snapshot: dict | None, max_age: int | None = None) -> bool:
    """True si la ubicación es reciente (por defecto 1 hora)."""
    if not snapshot:
        return False
    limit = config.LOCATION_MAX_AGE if max_age is None else max_age
    return time.time() - snapshot["timestamp"] <= limit


def effective(context) -> tuple[float, float] | None:
    """Coordenadas aproximadas si hay una ubicación reciente."""
    snapshot = get(context)
    if is_fresh(snapshot):
        return snapshot["lat"], snapshot["lon"]
    return None


def describe(snapshot: dict) -> str:
    return (
        f"{snapshot['lat']:.5f}, {snapshot['lon']:.5f} "
        f"(±{snapshot.get('approx_km')} km aprox.)"
    )
