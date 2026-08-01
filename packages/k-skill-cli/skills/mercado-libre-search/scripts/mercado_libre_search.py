#!/usr/bin/env python3
"""Busqueda de productos en Mercado Libre Mexico (MLM).

Fuente publica documentada: api.mercadolibre.com/sites/MLM/search (sin API key).
Desde IPs de datacenter/cloud puede devolver 403 (bloqueo por IP); desde IP
residencial funciona. En ese caso, remite al portal publico listado.mercadolibre.com.mx.

Uso:
  python3 mercado_libre_search.py --q "audifonos bluetooth" --limit 5
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

SEARCH_URL = "https://api.mercadolibre.com/sites/MLM/search"
USER_AGENT = "k-skill-mercado-libre-search/1.0 (+https://github.com/NomaDamas/k-skill)"
PORTAL_URL = "https://listado.mercadolibre.com.mx"


def fetch(query, limit):
    url = SEARCH_URL + "?" + urllib.parse.urlencode({"q": query, "limit": limit})
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise SystemExit(
                "Mercado Libre bloqueo la peticion (HTTP 403). El API publico es "
                f"accesible desde IP residencial; desde esta maquina usa el portal: {PORTAL_URL}/{urllib.parse.quote(query)}"
            ) from exc
        raise SystemExit(f"La API respondio HTTP {exc.code}.") from exc


def summarize(item):
    price = item.get("price")
    original = item.get("original_price")
    return {
        "titulo": item.get("title"),
        "precio_mxn": price,
        "precio_original_mxn": original,
        "descuento_pct": round((1 - price / original) * 100, 1) if price and original and original > 0 else None,
        "moneda": item.get("currency_id"),
        "condicion": item.get("condition"),
        "vendedor": item.get("seller") and item.get("seller").get("nickname"),
        "ubicacion": item.get("address") and item.get("address").get("city_name"),
        "link": item.get("permalink"),
    }


def main():
    parser = argparse.ArgumentParser(description="Busqueda de productos en Mercado Libre Mexico")
    parser.add_argument("--q", required=True, help="Busqueda")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    data = fetch(args.q, args.limit)
    items = data.get("results") or []
    if not items:
        raise SystemExit("No se encontraron productos para esa busqueda.")

    print(json.dumps(
        {
            "source": "api.mercadolibre.com (MLM)",
            "query": args.q,
            "total": data.get("paging", {}).get("total"),
            "results": [summarize(item) for item in items],
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
