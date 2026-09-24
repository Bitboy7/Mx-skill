"""Skill: búsqueda de productos y precios (mx-product-search, Liverpool)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def precio(update, context) -> str:
    query = " ".join(context.args).strip()
    if not query:
        ask("precio", "¿Qué producto quieres buscar? (ej. audífonos bluetooth)")
        return ""

    data = await runner.run_skill("mx-product-search", ["--q", query, "--limit", "5"])
    results = data.get("results") or []
    if not results:
        return "No se encontraron productos para esa búsqueda."

    lines = []
    for item in results:
        price = f"${item.get('precio_mxn'):,}" if item.get("precio_mxn") is not None else "N/D"
        discount = item.get("descuento_pct")
        disc = f"  ({discount}% dto)" if discount else ""
        marca = item.get("marca")
        marca_txt = f"{formatting.esc(marca)} · " if marca else ""
        lines.append(
            f"• <a href='{formatting.esc(item.get('link') or '')}'><b>{formatting.esc(item.get('titulo'))}</b></a>\n"
            f"  💲 <b>{price} MXN</b>{disc} · {marca_txt}{formatting.esc(str(item.get('rating') or ''))}"
        )
    return formatting.section(f"Productos: {query}", "\n".join(lines))


register(
    SkillEntry(
        command="precio",
        description="Busca productos y precios en Liverpool México",
        usage="/precio <producto>",
        handler=precio,
        skill_id="mx-product-search",
    )
)
