"""Skill: búsqueda y comparación de precios de productos (mx-product-search)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register


def _price(item) -> str:
    value = item.get("precio_mxn")
    if not isinstance(value, (int, float)):
        return "N/D"
    if float(value).is_integer():
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def _line(item) -> str:
    titulo = item.get("titulo") or "N/D"
    link = item.get("link") or ""
    enlace = f"<a href='{formatting.esc(link)}'>{formatting.esc(titulo)}</a>" if link else formatting.esc(titulo)
    discount = item.get("descuento_pct")
    disc = f" ({discount}% dto)" if discount else ""
    return f"  • {enlace} — <b>{_price(item)} MXN</b>{disc}"


async def precio(update, context) -> str:
    query = " ".join(context.args).strip()
    if not query:
        ask("precio", "¿Qué producto quieres buscar? (ej. audífonos bluetooth)")
        return ""

    data = await runner.run_skill("mx-product-search", ["--q", query, "--limit", "5"])
    por_tienda = data.get("por_tienda") or {}
    errores = data.get("errores") or {}

    lines = []
    for tienda, items in por_tienda.items():
        if not items:
            continue
        lines.append(f"<b>{formatting.esc(tienda)}</b>")
        lines.extend(_line(item) for item in items)

    if not lines:
        results = data.get("results") or []
        if not results:
            return f"No se encontraron productos para '{query}'."
        lines = [_line(item) for item in results]

    if errores:
        lines.append(f"<i>Sin datos de: {formatting.esc(', '.join(errores))}</i>")

    return formatting.section(f"Precios: {query}", "\n".join(lines))


register(
    SkillEntry(
        command="precio",
        description="Busca y compara precios de productos en tiendas mexicanas",
        usage="/precio <producto>",
        handler=precio,
        skill_id="mx-product-search",
    )
)
