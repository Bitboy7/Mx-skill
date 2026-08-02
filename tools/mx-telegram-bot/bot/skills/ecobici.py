"""Skill: Ecobici CDMX (ecobici-cdmx)."""

from .. import config, formatting, geo, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def ecobici(update, context) -> str:
    place = " ".join(context.args).strip()
    coords = geo.effective(context)

    if not place and not coords:
        ask("ecobici", "¿En qué colonia buscas Ecobici? (o comparte tu ubicación 📍)", kind="place")
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

    data = await runner.run_skill("ecobici-cdmx", skill_args)

    results = data.get("results") or []
    if not results:
        return "No hay estaciones de Ecobici en ese radio. Comparte tu ubicación (📎) o prueba otra colonia."

    lines = []
    for station in results:
        status = "🟢" if station.get("activa") else "🔴"
        lines.append(
            f"• {status} <b>{formatting.esc(station.get('estacion'))}</b> "
            f"({station.get('distancia_km')} km)\n"
            f"  🚲 {station.get('bicis_disponibles')} disponibles · "
            f"espacios {station.get('espacios_libres')}/{station.get('capacidad')}"
        )
    return formatting.section(f"Ecobici cerca de {label}", "\n".join(lines))


register(
    SkillEntry(
        command="ecobici",
        description="Estaciones de Ecobici CDMX con bicis disponibles cerca",
        usage="/ecobici <colonia o coordenadas>",
        handler=ecobici,
        skill_id="ecobici-cdmx",
    )
)
