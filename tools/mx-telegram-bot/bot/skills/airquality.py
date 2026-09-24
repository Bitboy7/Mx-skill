"""Skill: calidad del aire en México (mx-air-quality)."""

from .. import config, formatting, geo, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def aire(update, context) -> str:
    place = " ".join(context.args).strip()
    coords = geo.effective(context)

    if not place and not coords:
        ask("aire", "¿De qué ciudad quieres la calidad del aire? (o comparte tu ubicación 📍)", kind="place")
        return ""

    if place:
        skill_args = ["--place", place, "--json"]
        label = place
    elif coords:
        skill_args = ["--lat", str(coords[0]), "--lon", str(coords[1]), "--json"]
        label = "tu ubicación"
    else:
        skill_args = ["--place", config.DEFAULT_PLACE, "--json"]
        label = config.DEFAULT_PLACE

    data = await runner.run_skill("mx-air-quality", skill_args)
    calidad = data.get("calidad") or {}

    lines = [
        formatting.bullet("Índice US AQI", f"{calidad.get('indice_us_aqi') or 'N/D'} ({calidad.get('categoria') or 'N/D'})"),
        formatting.bullet("PM2.5", f"{calidad.get('pm2_5_ug_m3') or 'N/D'} µg/m³"),
        formatting.bullet("PM10", f"{calidad.get('pm10_ug_m3') or 'N/D'} µg/m³"),
        formatting.bullet("Medido", data.get("medido_en") or "N/D"),
    ]
    advice = calidad.get("recomendacion")
    place_name = (data.get("place") or {}).get("name") or label
    body = "\n".join(lines)
    if advice:
        body += f"\n\n{formatting.esc(advice)}"
    return formatting.section(f"Calidad del aire en {place_name}", body)


register(
    SkillEntry(
        command="aire",
        description="Calidad del aire (PM2.5, PM10, US AQI) de una ciudad de México",
        usage="/aire <ciudad>  (ej. /aire Monterrey)",
        handler=aire,
        skill_id="mx-air-quality",
    )
)
