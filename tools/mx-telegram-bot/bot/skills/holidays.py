"""Skill: días feriados de México (mx-holiday-calendar)."""

import re

from .. import formatting, runner
from .registry import SkillEntry, register

NEXT_WORDS = {"proximos", "próximos", "siguientes", "next"}


async def feriado(update, context) -> str:
    args = list(context.args)

    if args and args[0].lower() in NEXT_WORDS:
        skill_args = ["--next", "--json"]
        title = "Próximos días feriados"
    elif args and re.fullmatch(r"\d{4}", args[0]):
        skill_args = ["--year", args[0], "--json"]
        title = f"Días feriados {args[0]}"
    else:
        skill_args = ["--json"]
        title = "Días feriados de este año"

    data = await runner.run_skill("mx-holiday-calendar", skill_args)
    results = data.get("results") or []
    if not results:
        return "No se encontraron días feriados para ese periodo."

    lines = []
    for row in results:
        types = ", ".join(row.get("tipos") or []) or "Oficial"
        faltan = row.get("dias_faltantes")
        suffix = f" · en {faltan} días" if isinstance(faltan, int) and faltan >= 0 else ""
        lines.append(
            f"• <b>{formatting.esc(row.get('fecha'))}</b> — {formatting.esc(row.get('nombre_local'))} "
            f"<i>[{formatting.esc(types)}]</i>{suffix}"
        )
    return formatting.section(title, "\n".join(lines))


register(
    SkillEntry(
        command="feriado",
        description="Días feriados oficiales de México (año actual, un año o los próximos)",
        usage="/feriado  o  /feriado 2027  o  /feriado proximos",
        handler=feriado,
        skill_id="mx-holiday-calendar",
    )
)
