"""Skill: resultados de la Lotería Nacional / Melate (melate-results)."""

import re

from .. import formatting, runner
from .registry import SkillEntry, register


async def melate(update, context) -> str:
    args = list(context.args)
    numbers = [a for a in args if re.fullmatch(r"\d{1,2}", a)]

    if len(numbers) >= 6:
        data = await runner.run_skill(
            "melate-results", ["check", "--numbers", " ".join(numbers[:6])]
        )
        return (
            f"Sorteo <b>{formatting.esc(data.get('sorteo'))}</b> ({data.get('draw_date')})\n"
            f"Ganadores: <b>{formatting.esc(data.get('draw_numbers'))}</b>\n"
            f"Tus números: {formatting.esc(' '.join(map(str, data.get('user_numbers') or [])))}\n"
            f"Coincidencias: <b>{data.get('match_count')}/6</b> "
            f"({formatting.esc(' '.join(map(str, data.get('matching_numbers') or [])))})\n\n"
            f"Verificación oficial: {formatting.esc(data.get('official_checker'))}"
        )

    data = await runner.run_skill("melate-results", ["latest"])
    results = data.get("results") or []
    if not results:
        return "No se encontraron resultados."

    lines = []
    for game in results[:4]:
        entries = " | ".join(f"{e['label']}: {e['numbers']}" for e in game.get("entries") or [])
        lines.append(f"• <b>{formatting.esc(game.get('game'))}</b> (sorteo {game.get('sorteo')}, {game.get('draw_date')})\n  {entries}")
    return "Resultados oficiales de la Lotería Nacional:\n" + "\n\n".join(lines)


register(
    SkillEntry(
        command="melate",
        description="Resultados de Melate / Lotería Nacional, o verifica tus números",
        usage="/melate  o  /melate 6 14 21 32 40 49",
        handler=melate,
        skill_id="melate-results",
    )
)
