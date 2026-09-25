"""Skill: autos usados/seminuevos confiables (mx-used-car-search)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register


def _parse_args(context):
    parts = " ".join(context.args or []).split()
    estado = None
    if "en" in parts:
        idx = parts.index("en")
        estado = " ".join(parts[idx + 1:]).strip() or None
        parts = parts[:idx]
    marca = parts[0] if parts else None
    modelo = " ".join(parts[1:]).strip() or None
    return marca, modelo, estado


async def autos(update, context) -> str:
    marca, modelo, estado = _parse_args(context)
    if not marca:
        ask(
            "autos",
            "¿Qué auto buscas? Escribe marca y modelo, y opcionalmente el estado. "
            "Ej: 'nissan sentra' o 'toyota corolla en jalisco'.",
        )
        return ""

    skill_args = ["--marca", marca, "--limit", "6", "--json"]
    if modelo:
        skill_args += ["--modelo", modelo]
    if estado:
        skill_args += ["--estado", estado]

    data = await runner.run_skill("mx-used-car-search", skill_args)
    results = data.get("results") or []

    titulo = f"🚗 Autos usados: {marca} {modelo or ''}".strip()
    if estado:
        titulo += f" en {estado}"

    if not results:
        notice = data.get("notice") or "No se encontraron autos con esos criterios."
        encabezado = f"🚗 Sin resultados: {marca} {modelo or ''}".strip()
        return formatting.section(encabezado, f"<i>{formatting.esc(notice)}</i>")

    lines = []
    for item in results:
        precio = item.get("precio_mxn")
        km = item.get("km")
        fila = [
            f'• <a href="{formatting.esc(item.get("url"))}">{formatting.esc(item.get("titulo") or "Auto")}</a>',
            "   "
            + f"{'$' + format(item['precio_mxn'], ',') if precio else 'precio N/D'}"
            + f" · {item.get('anio') or 'año N/D'}"
            + f" · {format(km, ',') + ' km' if km else 'km N/D'}"
            + f" · {formatting.esc(item.get('ubicacion') or 'ubicación N/D')}"
            + f" · confianza {formatting.esc(item.get('confianza_nivel') or 'N/D')}"
            + f" ({item.get('confianza')})",
        ]
        for nota in (item.get("notas") or [])[:1]:
            fila.append(f"   ⚠️ {formatting.esc(nota)}")
        lines.append("\n".join(fila))

    body = "\n".join(lines)
    mediana = data.get("precio_mediana_mxn")
    if mediana:
        body += f"\n\n<i>Mediana del mercado: ${format(mediana, ',')} MXN</i>"
    body += "\n\nVerifica el NIV en REPUVE y los adeudos antes de comprar."
    return formatting.section(titulo, body)


register(
    SkillEntry(
        command="autos",
        description="Busca autos usados/seminuevos confiables en México (con índice de confianza)",
        usage="/autos <marca> [modelo] [en <estado>]  (ej. /autos nissan sentra en jalisco)",
        handler=autos,
        skill_id="mx-used-car-search",
    )
)
