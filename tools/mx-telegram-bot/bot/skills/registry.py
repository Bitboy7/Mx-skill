"""Registro central de comandos/skills del bot.

Cada módulo de skill define un `SkillEntry` y lo registra aquí. Añadir una skill
nueva = crear un módulo en este paquete que registre su `SkillEntry` (ver
`weather.py` como plantilla).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Awaitable, Callable

# El handler recibe (update, context) y devuelve la respuesta en texto/HTML.
Handler = Callable[..., Awaitable[str]]


@dataclass(frozen=True)
class SkillEntry:
    command: str
    description: str
    usage: str
    handler: Handler
    skill_id: str = field(default="")

    def __post_init__(self) -> None:
        # El handler declara a qué skill interna llama (para el catálogo IA).
        if not self.skill_id:
            object.__setattr__(self, "skill_id", self.command)


_REGISTRY: dict[str, SkillEntry] = {}


def register(entry: SkillEntry) -> None:
    if entry.command in _REGISTRY:
        raise ValueError(f"Comando duplicado: /{entry.command}")
    _REGISTRY[entry.command] = entry


def get_all() -> dict[str, SkillEntry]:
    return dict(_REGISTRY)
