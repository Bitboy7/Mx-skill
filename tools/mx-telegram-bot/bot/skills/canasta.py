"""Skill: precios de la canasta básica (precios-canasta)."""

from .. import formatting, runner
from .registry import SkillEntry, register


async def canasta(update, context) -> str:
    args = list(context.args)
    skill_args = ["--top", "10"]
    estado = None

    if args:
        # Si el primer token empieza con "--", lo pasamos tal cual; si no, es un estado.
        if args[0].startswith("--"):
            skill_args = args
        else:
            estado = " ".join(args)
            skill_args += ["--estado", estado]

    data = await runner.run_skill("precios-canasta", skill_args)
    results = data.get("results") or []
    if not results:
        return f"No hay datos de canasta básica{f' para {estado}' if estado else ''}."

    lines = [
        f"• <b>{formatting.esc(r.get('tienda') or 'N/D')}</b> · {formatting.esc(r.get('estado') or 'N/D')} · "
        f"${formatting.esc(r.get('costo_mxn'))}"
        for r in results
    ]
    title = f"Canasta básica más barata{f' en {estado}' if estado else ''}"
    return formatting.section(title, "\n".join(lines))


register(
    SkillEntry(
        command="canasta",
        description="Precios de la canasta básica por tienda y estado (PROFECO)",
        usage="/canasta  o  /canasta Jalisco",
        handler=canasta,
        skill_id="precios-canasta",
    )
)
