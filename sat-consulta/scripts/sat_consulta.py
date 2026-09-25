#!/usr/bin/env python3
"""Consulta servicios publicos del SAT (Mexico) sin e.firma.

Acciones (todas devuelven JSON por stdout):
  factura     Estatus de un CFDI (Vigente / Cancelado) via el servicio publico
              de validacion del SAT.
  69b         Busca un RFC en el listado 69-B (EFOS/EDOS).
  constancia  Lee la Constancia de Situacion Fiscal por QR (RFC + id_cif).
  catalogo    Catalogos oficiales del SAT (producto, regimen, uso CFDI, etc.).

No requiere credenciales. Usa la libreria `satcfdi` para 69b/constancia/catalogos
y el servicio SOAP publico para `factura`.

Uso:
  python3 sat_consulta.py --action factura --uuid <uuid> --rfc-emisor <rfc> \
      --rfc-receptor <rfc> --total 1250.30
  python3 sat_consulta.py --action 69b --rfc AAA010101AAA
  python3 sat_consulta.py --action constancia --rfc AAA010101AAA --id-cif 012345678
  python3 sat_consulta.py --action catalogo --tipo regimen --clave 601
  python3 sat_consulta.py --action catalogo --tipo producto --buscar software
"""

import argparse
import csv
import datetime
import io
import json
import sys
import urllib.error
import urllib.request
from xml.etree import ElementTree as ET

USER_AGENT = "mx-skill-sat-consulta/1.0"
SOAP_URL = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc"
SOAP_ACTION = "http://tempuri.org/IConsultaCFDIService/Consulta"
LISTADO_69B_CSV = "http://omawww.sat.gob.mx/cifras_sat/Documents/Listado_Completo_69-B.csv"

CATALOGOS = {
    "producto": ("C756_c_ClaveProdServ", "Clave de producto/servicio"),
    "unidad": ("C756_c_ClaveUnidad", "Clave de unidad"),
    "regimen": ("C756_c_RegimenFiscal", "Regimen fiscal"),
    "uso": ("C756_c_UsoCFDI", "Uso del CFDI"),
    "forma-pago": ("C756_c_FormaPago", "Forma de pago"),
    "metodo-pago": ("C756_c_MetodoPago", "Metodo de pago"),
    "moneda": ("C756_c_Moneda", "Moneda"),
    "pais": ("C756_c_Pais", "Pais"),
    "comprobante": ("C756_c_TipoDeComprobante", "Tipo de comprobante"),
}

ACCEPTED_ACTIONS = ("factura", "69b", "constancia", "catalogo")


# --------------------------------------------------------------------------- #
# Utilidades puras
# --------------------------------------------------------------------------- #
def _localname(tag):
    return tag.rsplit("}", 1)[-1]


def build_expresion(rfc_emisor, rfc_receptor, total, uuid):
    """Expresion impresa que espera el servicio publico de validacion."""
    return f"?re={rfc_emisor}&rr={rfc_receptor}&tt={total}&id={uuid}"


def build_soap_envelope(expresion):
    return (
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:tem="http://tempuri.org/">'
        "<soapenv:Header/>"
        "<soapenv:Body>"
        "<tem:Consulta>"
        f"<tem:expresionImpresa><![CDATA[{expresion}]]></tem:expresionImpresa>"
        "</tem:Consulta>"
        "</soapenv:Body>"
        "</soapenv:Envelope>"
    )


def parse_consulta_result(xml_bytes):
    """Extrae los campos de ConsultaResult del SOAP del SAT."""
    root = ET.fromstring(xml_bytes)
    for element in root.iter():
        if _localname(element.tag) == "ConsultaResult":
            return {
                _localname(child.tag): (child.text or "").strip()
                for child in element
            }
    return {}


def sanitize(value):
    """Convierte fechas y objetos de satcfdi a tipos serializables en JSON."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _descripcion_catalogo(value):
    if isinstance(value, (list, tuple)):
        return str(value[0]) if value else ""
    return str(value)


# --------------------------------------------------------------------------- #
# Acciones
# --------------------------------------------------------------------------- #
def consulta_factura(args):
    for campo in ("uuid", "rfc_emisor", "rfc_receptor", "total"):
        if not getattr(args, campo):
            raise ValueError(f"Falta el parametro --{campo.replace('_', '-')} para 'factura'.")

    uuid = args.uuid.strip().upper()
    rfc_emisor = args.rfc_emisor.strip().upper()
    rfc_receptor = args.rfc_receptor.strip().upper()
    total = str(args.total).strip()

    expresion = build_expresion(rfc_emisor, rfc_receptor, total, uuid)
    payload = build_soap_envelope(expresion).encode("utf-8")
    request = urllib.request.Request(
        SOAP_URL,
        data=payload,
        headers={
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPAction": f'"{SOAP_ACTION}"',
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"No se pudo consultar el servicio del SAT: {exc}") from exc

    result = parse_consulta_result(body)
    if not result:
        raise RuntimeError("El SAT devolvio una respuesta inesperada (sin ConsultaResult).")

    estado = result.get("Estado") or "No Encontrado"
    return {
        "action": "factura",
        "uuid": uuid,
        "rfc_emisor": rfc_emisor,
        "rfc_receptor": rfc_receptor,
        "total": total,
        "estado": estado,
        "vigente": estado.lower() == "vigente",
        "es_cancelable": result.get("EsCancelable") or None,
        "estatus_cancelacion": result.get("EstatusCancelacion") or None,
        "validacion_efos": result.get("ValidacionEFOS") or None,
        "codigo_estatus": result.get("CodigoEstatus") or None,
        "detalle": "Estatus reportado por el servicio publico de validacion del SAT.",
    }


def _fallback_69b(rfc):
    request = urllib.request.Request(LISTADO_69B_CSV, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read().decode("windows-1250", "ignore")
    lines = io.StringIO(content).read().splitlines(keepends=True)
    reader = csv.reader(lines[3:], delimiter=",", quotechar='"')
    for row in reader:
        if len(row) > 3 and row[1].strip().upper() == rfc:
            return row[3].strip() or "Presunto"
    return None


def consulta_69b(args):
    if not args.rfc:
        raise ValueError("Falta el parametro --rfc para '69b'.")
    rfc = args.rfc.strip().upper()

    from satcfdi.pacs.sat import SAT

    try:
        estado = SAT().list_69b(rfc)
        situacion = estado.value if estado is not None else None
    except Exception:  # noqa: BLE001 - cae al CSV directo si falla el cache/parseo
        situacion = _fallback_69b(rfc)

    encontrado = situacion is not None
    if encontrado:
        detalle = (
            f"El RFC aparece en el listado 69-B con situacion '{situacion}'. "
            "Revisa la publicacion oficial del SAT antes de operar con este contribuyente."
        )
    else:
        detalle = "El RFC no aparece en el listado 69-B (EFOS/EDOS) publicado por el SAT."
    return {
        "action": "69b",
        "rfc": rfc,
        "encontrado": encontrado,
        "situacion": situacion,
        "detalle": detalle,
    }


def consulta_constancia(args):
    if not args.rfc or not args.id_cif:
        raise ValueError("Falta --rfc y --id-cif para 'constancia'.")
    rfc = args.rfc.strip().upper()
    id_cif = args.id_cif.strip()

    from satcfdi import csf

    try:
        datos = csf.retrieve(rfc, id_cif)
    except ValueError:
        return {
            "action": "constancia",
            "rfc": rfc,
            "id_cif": id_cif,
            "encontrado": False,
            "detalle": "El RFC o el folio (id_cif) no son validos para el validador del SAT.",
        }

    return {
        "action": "constancia",
        "rfc": rfc,
        "id_cif": id_cif,
        "encontrado": True,
        "url": csf.url(rfc, id_cif),
        "datos": sanitize(datos),
    }


def consulta_catalogo(args):
    if not args.tipo:
        raise ValueError("Falta el parametro --tipo para 'catalogo'.")
    tipo = args.tipo.strip().lower()
    if tipo not in CATALOGOS:
        raise ValueError(f"Tipo de catalogo no soportado: {tipo}. Usa uno de: {', '.join(CATALOGOS)}.")
    if not args.clave and not args.buscar:
        raise ValueError("Especifica --clave (busqueda exacta) o --buscar (texto).")

    from satcfdi.catalogs import select_all

    table, label = CATALOGOS[tipo]
    data = select_all(table)

    if args.clave:
        clave = args.clave.strip()
        for key, value in data.items():
            if str(key).upper() == clave.upper():
                return {
                    "action": "catalogo",
                    "tipo": tipo,
                    "etiqueta": label,
                    "clave": str(key),
                    "descripcion": _descripcion_catalogo(value),
                    "encontrado": True,
                }
        return {
            "action": "catalogo",
            "tipo": tipo,
            "etiqueta": label,
            "clave": clave,
            "encontrado": False,
            "detalle": f"La clave '{clave}' no existe en el catalogo {label}.",
        }

    termino = args.buscar.strip().lower()
    resultados = []
    for key, value in data.items():
        descripcion = _descripcion_catalogo(value)
        if termino in descripcion.lower() or termino in str(key).lower():
            resultados.append({"clave": str(key), "descripcion": descripcion})
            if len(resultados) >= 25:
                break
    return {
        "action": "catalogo",
        "tipo": tipo,
        "etiqueta": label,
        "buscar": args.buscar,
        "encontrado": bool(resultados),
        "total": len(data),
        "resultados": resultados,
    }


HANDLERS = {
    "factura": consulta_factura,
    "69b": consulta_69b,
    "constancia": consulta_constancia,
    "catalogo": consulta_catalogo,
}


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    parser = argparse.ArgumentParser(description="Consulta servicios publicos del SAT (Mexico).")
    parser.add_argument("--action", required=True, choices=ACCEPTED_ACTIONS)
    parser.add_argument("--rfc", help="RFC (69b, constancia)")
    parser.add_argument("--id-cif", dest="id_cif", help="Folio id_cif del QR (constancia)")
    parser.add_argument("--uuid", help="Folio fiscal del CFDI (factura)")
    parser.add_argument("--rfc-emisor", dest="rfc_emisor", help="RFC emisor (factura)")
    parser.add_argument("--rfc-receptor", dest="rfc_receptor", help="RFC receptor (factura)")
    parser.add_argument("--total", help="Total del CFDI (factura)")
    parser.add_argument("--tipo", help="Tipo de catalogo (catalogo)")
    parser.add_argument("--clave", help="Clave exacta (catalogo)")
    parser.add_argument("--buscar", help="Texto a buscar en el catalogo (catalogo)")
    parser.add_argument("--json", action="store_true", help="Salida JSON (siempre activa)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = HANDLERS[args.action](args)
    except ImportError:
        print("Falta la dependencia satcfdi. Instala con: pip install satcfdi", file=sys.stderr)
        sys.exit(3)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    except Exception as exc:  # noqa: BLE001 - mensaje amigable para el bot
        print(f"Error consultando el SAT: {exc}", file=sys.stderr)
        sys.exit(3)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
