"""Skill: gasolineras baratas (gas-prices-mx)."""

from .. import config, formatting, geo, runner
from .registry import SkillEntry, register


async def gasolina(update, context) -> str:
    place = " ".join(context.args).strip()
    coords = geo.effective(context)

    if place:
        skill_args = ["--place", place, "--limit", "5"]
        label = place
    elif coords:
        skill_args = ["--lat", str(coords[0]), "--lon", str(coords[1]), "--limit", "5"]
        label = "tu ubicación"
    else:
        skill_args = ["--place", config.DEFAULT_PLACE, "--limit", "5"]
        label = config.DEFAULT_PLACE

    data = await runner.run_skill("gas-prices-mx", skill_args)

    results = data.get("results") or []
    if not results:
        return "No se encontraron gasolineras en ese radio (o la API de la CRE está fuera de servicio)."

    fuel = data.get("fuel") or "regular"
    lines = []
    for g in results:
        lines.append(
            f"• <b>{formatting.esc(g.get('razon_social') or g.get('calle') or 'N/D')}</b> · "
            f"${formatting.esc(g.get('precio'))}/L · {g.get('distancia_km')} km\n"
            f"  {formatting.esc(g.get('colonia') or '')}, {formatting.esc(g.get('municipio') or '')}, {formatting.esc(g.get('estado') or '')}"
        )
    return formatting.section(
        f"Gasolineras más baratas ({fuel}) cerca de {label}", "\n".join(lines)
    )


register(
    SkillEntry(
        command="gasolina",
        description="Gasolineras más baratas cerca de una ubicación (CRE)",
        usage="/gasolina <colonia/ciudad>",
        handler=gasolina,
        skill_id="gas-prices-mx",
    )
)
