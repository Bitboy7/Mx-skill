"""Skill: universidades y carreras de México (mx-university-search)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register

LIST_WORDS = {"todos", "todo", "lista", "listar"}


async def universidades(update, context) -> str:
    args = list(context.args)
    if not args:
        ask(
            "universidades",
            "¿Qué carrera o universidad buscas? (ej. medicina, UNAM, ingeniería). "
            "Escribe 'todos' para ver la lista.",
            kind="text",
        )
        return ""

    if args[0].lower() in LIST_WORDS:
        skill_args = ["--list", "--json"]
        title = "Universidades de México"
    else:
        query = " ".join(args)
        skill_args = ["--query", query, "--json"]
        title = f"Universidades para '{query}'"

    data = await runner.run_skill("mx-university-search", skill_args)
    results = data.get("results") or []
    if not results:
        return "No se encontraron universidades para esa búsqueda."

    lines = []
    for uni in results:
        carreras = ", ".join(uni.get("carreras") or [])
        lines.append(
            f"• <b>{formatting.esc(uni.get('nombre'))}</b> <i>[{formatting.esc(uni.get('tipo'))}]</i>\n"
            f"  {formatting.esc(uni.get('ciudad'))}, {formatting.esc(uni.get('estado'))}\n"
            f"  Carreras: {formatting.esc(carreras)}\n"
            f"  {formatting.esc(uni.get('sitio'))}"
        )
    return formatting.section(title, "\n\n".join(lines))


register(
    SkillEntry(
        command="universidades",
        description="Universidades de México y sus carreras, con enlaces oficiales",
        usage="/universidades <carrera o universidad>  (ej. /universidades medicina)  o  /universidades todos",
        handler=universidades,
        skill_id="mx-university-search",
    )
)
