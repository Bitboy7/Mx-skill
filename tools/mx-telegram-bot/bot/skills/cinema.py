"""Skill: cartelera de cine (cine-mx)."""

from .. import formatting, runner
from .registry import SkillEntry, register


async def cine(update, context) -> str:
    args = list(context.args)

    if args and args[0] in ("funciones", "functions"):
        if len(args) < 3:
            return "Uso: <code>/cine funciones &lt;id_cine&gt; &lt;id_pelicula&gt;</code>"
        data = await runner.run_skill("cine-mx", ["functions", "--cinema", args[1], "--movie", args[2]])
        funcs = data.get("results") or []
        if not funcs:
            return "No se encontraron funciones."
        lines = [
            f"• {formatting.esc(f.get('fecha'))} · sala {f.get('sala')} · pantalla {f.get('pantalla')} · {f.get('disponibilidad')}"
            for f in funcs[:8]
        ]
        return formatting.section(f"Funciones (película {data.get('movie')})", "\n".join(lines))

    data = await runner.run_skill("cine-mx", ["movies"])
    movies = data.get("results") or []
    if not movies:
        return "No se pudo obtener la cartelera de Cinemex."
    lines = [
        f"• <b>{formatting.esc(m.get('titulo'))}</b> · {formatting.esc(' / '.join(m.get('genero') or []))} · {m.get('duracion_min')}"
        for m in movies[:10]
    ]
    return (
        formatting.section("Cartelera de Cinemex", "\n".join(lines))
        + "\n\n<i>Cinepolis: consulta el portal oficial (su API no es pública estable).</i>"
    )


register(
    SkillEntry(
        command="cine",
        description="Cartelera de cine en México (Cinemex) y funciones",
        usage="/cine  o  /cine funciones <id_cine> <id_pelicula>",
        handler=cine,
        skill_id="cine-mx",
    )
)
