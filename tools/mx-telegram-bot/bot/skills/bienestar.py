"""Skill: Programas para el Bienestar (beneficios-programas)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register

LIST_WORDS = {"todos", "todo", "lista", "listar"}


async def bienestar(update, context) -> str:
    args = list(context.args)
    if not args:
        ask(
            "bienestar",
            "¿Qué apoyo o programa buscas? (ej. pensión, beca, jóvenes, campo). "
            "Escribe 'todos' para ver la lista.",
            kind="text",
        )
        return ""

    if args[0].lower() in LIST_WORDS:
        skill_args = ["--list", "--json"]
        title = "Programas para el Bienestar"
    else:
        query = " ".join(args)
        skill_args = ["--query", query, "--json"]
        title = f"Programas para '{query}'"

    data = await runner.run_skill("beneficios-programas", skill_args)
    results = data.get("results") or []
    if not results:
        return (
            f"No se encontraron programas para esa búsqueda. Consulta "
            f"{formatting.esc(data.get('portal'))}"
        )

    lines = []
    for program in results:
        requisitos = "\n".join(f"    - {formatting.esc(r)}" for r in program.get("requisitos") or [])
        lines.append(
            f"• <b>{formatting.esc(program.get('nombre'))}</b> <i>[{formatting.esc(program.get('categoria'))}]</i>\n"
            f"  Apoyo: {formatting.esc(program.get('apoyo'))}\n"
            f"  Monto: {formatting.esc(program.get('monto'))}\n"
            f"  Requisitos:\n{requisitos}\n"
            f"  {formatting.esc(program.get('enlace'))}"
        )
    return formatting.section(title, "\n\n".join(lines))


register(
    SkillEntry(
        command="bienestar",
        description="Programas para el Bienestar de México: requisitos, apoyos y enlaces oficiales",
        usage="/bienestar <tema>  (ej. /bienestar pensión)  o  /bienestar todos",
        handler=bienestar,
        skill_id="beneficios-programas",
    )
)
