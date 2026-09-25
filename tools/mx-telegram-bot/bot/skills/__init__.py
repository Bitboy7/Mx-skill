"""Paquete de skills del bot. Importar este paquete registra todas las skills."""

from .registry import SkillEntry, get_all  # noqa: F401

from . import (  # noqa: F401,E402  (el orden importa para registrar sin duplicados)
    airquality,
    autos,
    bienestar,
    canasta,
    cinema,
    ecobici,
    gas,
    holidays,
    ine,
    jobs,
    licitaciones,
    lottery,
    news,
    products,
    realestate,
    restroom,
    rfc,
    sat,
    shipping,
    sports,
    transit,
    universities,
    weather,
    zipcode,
)


def list_skills() -> dict[str, SkillEntry]:
    return get_all()
