"""Skill: clima en México (mx-weather)."""

from .. import config, formatting, geo, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def clima(update, context) -> str:
    place = " ".join(context.args).strip()
    coords = geo.effective(context)

    if not place and not coords:
        ask("clima", "¿Para qué ciudad quieres el clima? (o comparte tu ubicación 📍)", kind="place")
        return ""

    if place:
        skill_args = ["--place", place, "--days", "3"]
        label = place
    elif coords:
        skill_args = ["--lat", str(coords[0]), "--lon", str(coords[1]), "--days", "3"]
        label = "tu ubicación"
    else:
        skill_args = ["--place", config.DEFAULT_PLACE, "--days", "3"]
        label = config.DEFAULT_PLACE

    data = await runner.run_skill("mx-weather", skill_args)

    actual = data.get("actual") or {}
    lines = [
        formatting.bullet("Temperatura", f"{actual.get('temp_c') or 'N/D'} °C"),
        formatting.bullet("Humedad", f"{actual.get('humedad_pct') or 'N/D'} %"),
        formatting.bullet("Viento", f"{actual.get('viento_kmh') or 'N/D'} km/h"),
        formatting.bullet("Descripción", actual.get("descripcion") or "N/D"),
    ]
    pronostico = []
    for day in (data.get("pronostico") or [])[:3]:
        pronostico.append(
            f"• {day.get('fecha')}: {day.get('min_c') or 'N/D'}–{day.get('max_c') or 'N/D'} °C · "
            f"lluvia {day.get('prob_lluvia_pct') or 'N/D'}% · {day.get('descripcion') or 'N/D'}"
        )

    place_name = (data.get("place") or {}).get("name") or label
    header = formatting.section(f"Clima en {place_name}", "\n".join(lines))
    return header + "\n\nPróximos días:\n" + "\n".join(pronostico)


register(
    SkillEntry(
        command="clima",
        description="Clima actual y pronóstico de una ciudad de México",
        usage="/clima <ciudad>  (ej. /clima Guadalajara)",
        handler=clima,
        skill_id="mx-weather",
    )
)
