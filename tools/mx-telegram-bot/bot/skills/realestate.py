"""Skill: inmuebles en México (mx-real-estate)."""

from .. import formatting, runner
from .registry import SkillEntry, register


async def inmuebles(update, context) -> str:
    args = list(context.args)
    tipo = "venta"
    if args and args[0] in ("renta", "venta"):
        tipo = args.pop(0)
    query = " ".join(args).strip()
    if not query:
        return "Uso: <code>/inmuebles [renta|venta] &lt;búsqueda&gt;</code>  (ej. /inmuebles renta departamento polanco)"

    data = await runner.run_skill("mx-real-estate", ["--q", query, "--tipo", tipo, "--limit", "5"])
    results = data.get("results") or []
    if not results:
        return "No se encontraron inmuebles (o Mercado Libre bloqueó la petición desde este servidor)."

    lines = []
    for item in results:
        attrs = []
        if item.get("dormitorios"):
            attrs.append(f"{item.get('dormitorios')} rec.")
        if item.get("banos"):
            attrs.append(f"{item.get('banos')} baños")
        if item.get("superficie_m2"):
            attrs.append(item.get("superficie_m2"))
        lines.append(
            f"• <a href='{formatting.esc(item.get('link') or '')}'><b>{formatting.esc(item.get('titulo'))}</b></a>\n"
            f"  💲 <b>{formatting.esc(item.get('precio'))}</b> · {formatting.esc(' · '.join(attrs))} · {formatting.esc(item.get('ubicacion') or '')}"
        )
    return formatting.section(f"Inmuebles ({tipo}): {query}", "\n".join(lines))


register(
    SkillEntry(
        command="inmuebles",
        description="Inmuebles en renta o venta en México",
        usage="/inmuebles [renta|venta] <búsqueda>",
        handler=inmuebles,
        skill_id="mx-real-estate",
    )
)
