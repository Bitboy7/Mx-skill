#!/usr/bin/env python3
"""Busca licitaciones y contrataciones públicas de México.

Fuente principal: API pública de solo lectura **LicitIA Abierto**
(https://api.licitia.com.mx/api/open/v1), que normaliza los datos que el
gobierno publica en Compras MX (antes CompraNet). Sin autenticación ni API key,
licencia CC BY 4.0 (atribución obligatoria).

Fallback: enlaces oficiales de Compras MX y Datos Abiertos cuando la API publica
no responde.

Uso:
  python3 compranet_search.py "software"
  python3 compranet_search.py "obra publica" --limit 10 --json
  python3 compranet_search.py "medicamentos" --year 2026 --estatus VIGENTE
"""

import argparse
import json
import urllib.parse
import urllib.request

LICITIA_URL = "https://api.licitia.com.mx/api/open/v1/licitaciones"
USER_AGENT = "k-skill-compranet-search/1.0 (+https://github.com/NomaDamas/k-skill)"
ATTRIBUTION = "LicitIA Abierto (CC BY 4.0) sobre datos públicos de Compras MX"

OFFICIAL_LINKS = {
    "comprasmx_difusion": "https://comprasmx.buengobierno.gob.mx/sitiopublico/#/",
    "comprasmx_datos_abiertos": "https://comprasmx.buengobierno.gob.mx/datos-abiertos",
    "historico_compranet": "https://historico-compranet.buengobierno.gob.mx/",
}


def http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def build_params(query, limit, year=None, tipo=None, estatus=None):
    params = {"q": query, "limit": limit}
    if year:
        params["anio"] = year
    if tipo:
        params["tipo"] = tipo
    if estatus:
        params["estatus"] = estatus
    return params


def normalize_item(item):
    return {
        "numero": item.get("numero_procedimiento"),
        "nombre": item.get("nombre_procedimiento"),
        "dependencia": item.get("dependencia"),
        "tipo": item.get("tipo_procedimiento"),
        "estatus": item.get("estatus"),
        "anio": item.get("anio_ejercicio"),
        "fecha_publicacion": item.get("fecha_publicacion"),
        "adjudicaciones": item.get("adjudicaciones"),
        "url_oficial": item.get("source_url"),
        "url_fuente": item.get("licitia_url") or item.get("fuente"),
    }


def fetch_licitaciones(query, limit, year=None, tipo=None, estatus=None):
    params = build_params(query, limit, year, tipo, estatus)
    url = LICITIA_URL + "?" + urllib.parse.urlencode(params)
    payload = http_get_json(url)
    if not payload.get("success", True):
        return []
    return [normalize_item(item) for item in (payload.get("data") or [])]


def build_payload(query, results, error=None):
    payload = {
        "source": ATTRIBUTION,
        "query": query,
        "results": results,
        "official_links": OFFICIAL_LINKS,
    }
    if error:
        payload["notice"] = (
            "No se pudo consultar la API pública de contrataciones; usa los enlaces oficiales. "
            f"Detalle: {error}"
        )
    return payload


def format_text(payload):
    lines = [f"Licitaciones para '{payload.get('query')}':"]
    results = payload.get("results") or []
    if not results:
        lines.append("• Sin resultados en la API pública.")
    for row in results:
        lines.append(
            f"• {row.get('nombre')} ({row.get('numero')})\n"
            f"  {row.get('dependencia')} · {row.get('tipo')} · {row.get('estatus')}\n"
            f"  {row.get('url_oficial') or row.get('url_fuente')}"
        )
    lines.append("")
    lines.append("Fuente: " + payload.get("source", ""))
    lines.append("Oficial: " + OFFICIAL_LINKS["comprasmx_difusion"])
    if payload.get("notice"):
        lines.append(payload["notice"])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Licitaciones públicas de México (Compras MX / LicitIA)")
    parser.add_argument("query", nargs="?", help="Palabra clave a buscar")
    parser.add_argument("--query", dest="query_opt", help="Palabra clave (alternativa posicional)")
    parser.add_argument("--limit", type=int, default=5, help="Número de resultados (1-50)")
    parser.add_argument("--year", type=int, default=None, help="Año de ejercicio")
    parser.add_argument("--tipo", default=None, help="Tipo de procedimiento")
    parser.add_argument("--estatus", default=None, help="Estatus (ej. VIGENTE, ADJUDICADO)")
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args(argv)

    query = (args.query_opt or args.query or "").strip()
    if not query:
        parser.error("Proporciona una palabra clave (posicional o --query).")
    if not 1 <= args.limit <= 50:
        parser.error("--limit debe estar entre 1 y 50")

    try:
        results = fetch_licitaciones(query, args.limit, args.year, args.tipo, args.estatus)
        payload = build_payload(query, results)
    except Exception as exc:  # noqa: BLE001
        payload = build_payload(query, [], error=str(exc))

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))


if __name__ == "__main__":
    main()
