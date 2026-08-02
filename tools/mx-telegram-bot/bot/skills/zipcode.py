"""Skill: código postal de México (mx-zipcode-search)."""

import re

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def codigo_postal(update, context) -> str:
    cp = (context.args[0] if context.args else "").strip()
    if not re.fullmatch(r"\d{5}", cp):
        ask("cp", "Escribe el código postal de 5 dígitos (ej. 06600).")
        return ""

    data = await runner.run_skill("mx-zipcode-search", [cp])
    places = data.get("places") or []
    lines = [formatting.bullet("Estado", data.get("estado") or "N/D")]
    colonias = " | ".join(p.get("colonia") or "" for p in places) or "N/D"
    lines.append(f"• Colonias: <b>{formatting.esc(colonias)}</b>")
    return formatting.section(f"CP {data.get('cp')}", "\n".join(lines))


register(
    SkillEntry(
        command="cp",
        description="Colonias, municipio y estado de un código postal de México",
        usage="/cp <código postal>  (ej. /cp 06600)",
        handler=codigo_postal,
        skill_id="mx-zipcode-search",
    )
)
