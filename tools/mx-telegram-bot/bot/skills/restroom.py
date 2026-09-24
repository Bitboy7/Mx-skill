"""Skill: baños públicos cerca (mx-restroom-nearby)."""

from .. import config, formatting, geo, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def banos(update, context) -> str:
    place = " ".join(context.args).strip()
    coords = geo.effective(context)

    if not place and not coords:
        ask("banos", "¿Cerca de dónde buscas baños públicos? (o comparte tu ubicación 📍)", kind="place")
        return ""

    if place:
        skill_args = ["--place", place, "--limit", "5", "--json"]
        label = place
    elif coords:
        skill_args = ["--lat", str(coords[0]), "--lon", str(coords[1]), "--limit", "5", "--json"]
        label = "tu ubicación"
    else:
        skill_args = ["--place", config.DEFAULT_PLACE, "--limit", "5", "--json"]
        label = config.DEFAULT_PLACE

    data = await runner.run_skill("mx-restroom-nearby", skill_args, timeout=150.0)
    results = data.get("results") or []
    if not results:
        return (
            f"No se encontraron baños públicos cerca de {formatting.esc(label)} en "
            f"{data.get('radio_m')} m. Comparte tu ubicación (📎) o prueba otro lugar."
        )

    lines = []
    for row in results:
        details = [row.get("costo"), row.get("acceso")]
        details = " · ".join(d for d in details if d)
        lines.append(
            f"• <b>{formatting.esc(row.get('nombre'))}</b> ({row.get('distancia_km')} km)\n"
            f"  {formatting.esc(details)}\n"
            f"  📍 {formatting.esc(row.get('mapa'))}"
        )
    return formatting.section(f"Baños públicos cerca de {label}", "\n".join(lines))


register(
    SkillEntry(
        command="banos",
        description="Baños públicos cerca de una ubicación (OpenStreetMap)",
        usage="/banos <lugar o coordenadas>  (ej. /banos Zócalo CDMX)",
        handler=banos,
        skill_id="mx-restroom-nearby",
    )
)
