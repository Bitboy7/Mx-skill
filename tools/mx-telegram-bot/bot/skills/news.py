"""Skill: noticias de México (mx-news)."""

from .. import formatting, runner
from .registry import SkillEntry, register


async def noticias(update, context) -> str:
    query = " ".join(context.args).strip()
    if query:
        data = await runner.run_skill("mx-news", ["search", "--q", query, "--limit", "8"])
        title = f"Noticias: {query}"
    else:
        data = await runner.run_skill("mx-news", ["top", "--limit", "8"])
        title = "Portada de noticias en México"

    results = data.get("results") or []
    if not results:
        return "No se encontraron noticias."

    lines = []
    for item in results[:8]:
        lines.append(
            f"• <a href='{formatting.esc(item.get('link', ''))}'>{formatting.esc(item.get('titulo'))}</a>\n"
            f"  <i>{formatting.esc(item.get('fuente'))} · {formatting.esc(item.get('fecha'))}</i>"
        )
    return formatting.section(title, "\n".join(lines))


register(
    SkillEntry(
        command="noticias",
        description="Portada o búsqueda de noticias de México",
        usage="/noticias  o  /noticias <palabra clave>",
        handler=noticias,
        skill_id="mx-news",
    )
)
