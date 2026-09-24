"""Skill: licitaciones públicas de México (compranet-search)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def licitaciones(update, context) -> str:
    query = " ".join(context.args).strip()
    if not query:
        ask("licitaciones", "¿Qué licitación o contratación buscas? (palabra clave, ej. software, obra)", kind="text")
        return ""

    data = await runner.run_skill("compranet-search", ["--query", query, "--limit", "5", "--json"])
    results = data.get("results") or []

    if not results:
        notice = data.get("notice")
        message = f"No se encontraron licitaciones para '{formatting.esc(query)}'."
        if notice:
            message += f"\n\n{formatting.esc(notice)}"
        return message

    lines = []
    for row in results:
        url = row.get("url_oficial") or row.get("url_fuente")
        lines.append(
            f"• <b>{formatting.esc(row.get('nombre'))}</b>\n"
            f"  {formatting.esc(row.get('numero'))}\n"
            f"  {formatting.esc(row.get('dependencia'))}\n"
            f"  {formatting.esc(row.get('tipo'))} · {formatting.esc(row.get('estatus'))}\n"
            f"  {formatting.esc(url)}"
        )
    return formatting.section(f"Licitaciones para '{query}'", "\n\n".join(lines))


register(
    SkillEntry(
        command="licitaciones",
        description="Licitaciones y contrataciones públicas de México (Compras MX)",
        usage="/licitaciones <palabra clave>  (ej. /licitaciones software)",
        handler=licitaciones,
        skill_id="compranet-search",
    )
)
