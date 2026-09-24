"""Skill: gasolineras baratas (gas-prices-mx)."""

from .. import config, formatting, geo, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def gasolina(update, context) -> str:
    place = " ".join(context.args).strip()
    coords = geo.effective(context)

    if not place and not coords:
        ask("gasolina", "¿Dónde buscas gasolina barata? (o comparte tu ubicación 📍)", kind="place")
        return ""

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
        return "No se encontraron gasolineras en ese radio (o la publicación de la CRE está fuera de servicio)."

    fuel = data.get("fuel") or "regular"
    lines = []
    for g in results:
        nombre = g.get("nombre") or g.get("razon_social") or "N/D"
        mapa = g.get("mapa") or ""
        enlace = f"<a href='{formatting.esc(mapa)}'><b>{formatting.esc(nombre)}</b></a>" if mapa else f"<b>{formatting.esc(nombre)}</b>"
        lines.append(
            f"• {enlace}\n"
            f"  💲 <b>${formatting.esc(g.get('precio'))}/L</b> · {g.get('distancia_km')} km"
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
