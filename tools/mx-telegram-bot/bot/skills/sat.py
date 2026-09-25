"""Skills: consultas publicas del SAT (sat-consulta).

Todas las acciones usan servicios publicos del SAT y no requieren e.firma.
"""

import re

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register

SAT_CATALOGOS = {
    "producto": "clave de producto/servicio",
    "unidad": "clave de unidad",
    "regimen": "regimen fiscal",
    "uso": "uso del CFDI",
    "forma-pago": "forma de pago",
    "metodo-pago": "metodo de pago",
    "moneda": "moneda",
    "pais": "pais",
    "comprobante": "tipo de comprobante",
}

_CLAVE_RE = re.compile(r"^[A-Za-z0-9-]{1,8}$")


def _parts(context) -> list[str]:
    return " ".join(context.args or []).split()


def _parece_clave(value: str) -> bool:
    """Heurística: ¿el valor es una clave de catálogo o texto libre?"""
    v = value.strip()
    if not _CLAVE_RE.fullmatch(v):
        return False
    if v.isdigit():
        return True
    if len(v) <= 3:
        return True
    # Códigos mixtos de 4 caracteres (p. ej. uso de CFDI: CP01, CN01, G01).
    return len(v) == 4 and any(c.isdigit() for c in v)


def _parse_qr(text: str) -> tuple[str, str] | None:
    """Extrae (rfc, id_cif) de una URL del validador QR del SAT (?D3=<id_cif>_<rfc>)."""
    from urllib.parse import parse_qs, urlparse

    query = parse_qs(urlparse(text).query)
    d3 = (query.get("D3") or [""])[0]
    if "_" not in d3:
        return None
    id_cif, rfc = d3.rsplit("_", 1)
    if not id_cif or not rfc:
        return None
    return rfc.strip().upper(), id_cif.strip()


async def sat_factura(update, context) -> str:
    parts = _parts(context)
    if len(parts) < 4:
        ask(
            "sat_factura",
            "Escribe los 4 datos del CFDI en una linea: "
            "<UUID> <RFC emisor> <RFC receptor> <total>. Ej: "
            "11111111-1111-1111-1111-111111111111 AAA010101AAA BBB010101BBB 1250.30",
        )
        return ""

    uuid, rfc_emisor, rfc_receptor, total = parts[0], parts[1], parts[2], parts[3]
    data = await runner.run_skill(
        "sat-consulta",
        [
            "--action", "factura",
            "--uuid", uuid,
            "--rfc-emisor", rfc_emisor,
            "--rfc-receptor", rfc_receptor,
            "--total", total,
            "--json",
        ],
    )

    estado = data.get("estado") or "N/D"
    if data.get("vigente"):
        titulo = "✅ CFDI VIGENTE"
    elif str(estado).strip().lower() == "cancelado":
        titulo = "🚫 CFDI CANCELADO"
    else:
        titulo = f"❓ CFDI: {estado}"

    lines = [
        formatting.bullet("UUID", data.get("uuid")),
        formatting.bullet("RFC emisor", data.get("rfc_emisor")),
        formatting.bullet("RFC receptor", data.get("rfc_receptor")),
        formatting.bullet("Total", data.get("total")),
        formatting.bullet("Estado", estado),
    ]
    for key, label in (
        ("es_cancelable", "Cancelable"),
        ("estatus_cancelacion", "Estatus cancelacion"),
        ("validacion_efos", "Validacion EFOS"),
        ("codigo_estatus", "Codigo"),
    ):
        if data.get(key):
            lines.append(formatting.bullet(label, data.get(key)))
    return formatting.section(titulo, "\n".join(lines))


async def sat_69b(update, context) -> str:
    rfc = " ".join(context.args or []).strip().upper()
    if not rfc:
        ask("sat_69b", "Escribe el RFC a buscar en el listado 69-B (EFOS/EDOS).")
        return ""

    data = await runner.run_skill(
        "sat-consulta", ["--action", "69b", "--rfc", rfc, "--json"]
    )
    if data.get("encontrado"):
        titulo = "⚠️ RFC en el listado 69-B"
    else:
        titulo = "✅ RFC no listado en 69-B"
    lines = [
        formatting.bullet("RFC", data.get("rfc")),
        formatting.bullet("Situacion", data.get("situacion") or "No aparece"),
        f"<i>{formatting.esc(data.get('detalle') or '')}</i>",
    ]
    return formatting.section(titulo, "\n".join(lines))


async def sat_constancia(update, context) -> str:
    parts = _parts(context)
    parsed = None
    if len(parts) == 1 and "D3=" in parts[0]:
        parsed = _parse_qr(parts[0])
    elif len(parts) >= 2:
        parsed = (parts[0].strip().upper(), parts[1].strip())

    if parsed is None:
        ask(
            "sat_constancia",
            "Escribe el RFC y el folio (id_cif) de la constancia, o pega la URL del QR. "
            "Ej: AAA010101AAA 012345678",
        )
        return ""

    rfc, id_cif = parsed
    data = await runner.run_skill(
        "sat-consulta",
        ["--action", "constancia", "--rfc", rfc, "--id-cif", id_cif, "--json"],
    )

    if not data.get("encontrado"):
        return formatting.section(
            "❓ Constancia no encontrada",
            f"<i>{formatting.esc(data.get('detalle') or '')}</i>",
        )

    datos = data.get("datos") or {}
    lines: list[str] = []
    for key, value in datos.items():
        if key == "Regimenes" and isinstance(value, list):
            for regimen in value:
                if isinstance(regimen, dict):
                    lines.append(formatting.bullet("Regimen", regimen.get("RegimenFiscal") or "N/D"))
                    if regimen.get("Fecha de alta"):
                        lines.append(formatting.bullet("Alta", regimen.get("Fecha de alta")))
                else:
                    lines.append(formatting.bullet("Regimen", regimen))
        elif isinstance(value, (list, dict)):
            continue
        else:
            lines.append(formatting.bullet(key, value or "N/D"))

    if data.get("url"):
        lines.append(f"<a href=\"{formatting.esc(data.get('url'))}\">Ver en el SAT</a>")
    return formatting.section("🧾 Constancia de situacion fiscal", "\n".join(lines))


async def sat_catalogo(update, context) -> str:
    parts = _parts(context)
    if not parts:
        ask(
            "sat_catalogo",
            "Escribe el catalogo y la clave o texto. Ej: 'regimen 601' o 'producto software'. "
            f"Catalogos: {', '.join(SAT_CATALOGOS)}.",
        )
        return ""

    tipo = parts[0].strip().lower()
    valor = " ".join(parts[1:]).strip()
    if tipo not in SAT_CATALOGOS:
        return formatting.section(
            "Catalogo no soportado",
            f"Tipos validos: {formatting.esc(', '.join(SAT_CATALOGOS))}",
        )
    if not valor:
        ask("sat_catalogo", f"¿Que clave o texto buscas en el catalogo de {SAT_CATALOGOS[tipo]}?")
        return ""

    skill_args = ["--action", "catalogo", "--tipo", tipo, "--json"]
    skill_args += ["--clave", valor] if _parece_clave(valor) else ["--buscar", valor]
    data = await runner.run_skill("sat-consulta", skill_args)

    etiqueta = data.get("etiqueta") or SAT_CATALOGOS[tipo]
    if data.get("descripcion") is not None:
        body = "\n".join(
            [
                formatting.bullet("Clave", data.get("clave")),
                formatting.bullet("Descripcion", data.get("descripcion")),
            ]
        )
        return formatting.section(f"📚 Catalogo: {etiqueta}", body)

    resultados = data.get("resultados") or []
    if not resultados:
        return formatting.section(
            "📚 Sin resultados",
            f"No se encontro '{formatting.esc(valor)}' en el catalogo de {formatting.esc(etiqueta)}.",
        )

    lines = [
        f"• <code>{formatting.esc(r.get('clave'))}</code> — {formatting.esc(r.get('descripcion'))}"
        for r in resultados
    ]
    return formatting.section(f"📚 Catalogo: {etiqueta} (primeros {len(lines)})", "\n".join(lines))


register(
    SkillEntry(
        command="sat_factura",
        description="Verifica el estatus de un CFDI en el SAT (vigente/cancelado)",
        usage="/sat_factura <UUID> <RFC emisor> <RFC receptor> <total>",
        handler=sat_factura,
        skill_id="sat-consulta",
    )
)
register(
    SkillEntry(
        command="sat_69b",
        description="Busca un RFC en el listado 69-B del SAT (EFOS/EDOS)",
        usage="/sat_69b <RFC>  (ej. /sat_69b AAA010101AAA)",
        handler=sat_69b,
        skill_id="sat-consulta",
    )
)
register(
    SkillEntry(
        command="sat_constancia",
        description="Lee la Constancia de Situacion Fiscal por QR (RFC + folio id_cif)",
        usage="/sat_constancia <RFC> <id_cif>  (o pega la URL del QR)",
        handler=sat_constancia,
        skill_id="sat-consulta",
    )
)
register(
    SkillEntry(
        command="sat_catalogo",
        description="Consulta catalogos del SAT (producto, regimen, uso CFDI, unidad, etc.)",
        usage="/sat_catalogo <tipo> <clave|texto>  (ej. /sat_catalogo regimen 601)",
        handler=sat_catalogo,
        skill_id="sat-consulta",
    )
)
