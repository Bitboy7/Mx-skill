"""Skill: búsqueda en Mercado Libre México (mercado-libre-search)."""

from .. import formatting, runner
from .registry import SkillEntry, register


async def precio(update, context) -> str:
    query = " ".join(context.args).strip()
    if not query:
        return "Uso: <code>/precio &lt;producto&gt;</code>  (ej. /precio audifonos bluetooth)"

    data = await runner.run_skill("mercado-libre-search", ["--q", query, "--limit", "5"])
    results = data.get("results") or []
    if not results:
        return "No se encontraron productos en Mercado Libre."

    lines = []
    for item in results:
        price = f"${item.get('precio_mxn')}" if item.get("precio_mxn") is not None else "N/D"
        discount = item.get("descuento_pct")
        disc = f"  ({discount}% dto)" if discount else ""
        link = item.get("link") or ""
        lines.append(
            f"• <a href='{formatting.esc(link)}'><b>{formatting.esc(item.get('titulo'))}</b></a>\n"
            f"  💲 <b>{price} MXN</b>{disc} · {formatting.esc(item.get('condicion'))} · {formatting.esc(item.get('ubicacion') or '')}"
        )
    return formatting.section(f"Mercado Libre: {query}", "\n".join(lines))


register(
    SkillEntry(
        command="precio",
        description="Busca productos y precios en Mercado Libre México",
        usage="/precio <producto>",
        handler=precio,
        skill_id="mercado-libre-search",
    )
)
