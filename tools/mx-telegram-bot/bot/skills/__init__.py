"""Paquete de skills del bot. Importar este paquete registra todas las skills."""

from .registry import SkillEntry, get_all  # noqa: F401

from . import (  # noqa: F401,E402  (el orden importa para registrar sin duplicados)
    airquality,
    bienestar,
    canasta,
    cinema,
    ecobici,
    gas,
    holidays,
    ine,
    licitaciones,
    lottery,
    marketplace,
    news,
    realestate,
    restroom,
    rfc,
    shipping,
    sports,
    transit,
    weather,
    zipcode,
)


def list_skills() -> dict[str, SkillEntry]:
    return get_all()
