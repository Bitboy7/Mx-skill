#!/usr/bin/env python3
"""Busqueda de inmuebles en Mexico (renta/venta) via Mercado Libre Inmuebles.

Fuente publica documentada: api.mercadolibre.com/sites/MLM/search con la
categoria de Inmuebles. Sin API key; desde IP residencial funciona, desde IP
de datacenter puede dar 403. Portales alternativos: Vivanuncios, Inmuebles24,
Propiedades.com (todos con proteccion anti-bot; se documentan como fallback).

Uso:
  python3 mx_real_estate.py --q "departamento polanco renta" --tipo venta
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

SEARCH_URL = "https://api.mercadolibre.com/sites/MLM/search"
USER_AGENT = "k-skill-mx-real-estate/1.0 (+https://github.com/NomaDamas/k-skill)"
CATEGORIES = {"venta": "MLM1459", "renta": "MLM1457"}
PORTALS = [
    "https://www.vivanuncios.com.mx/",
    "https://www.inmuebles24.com/",
    "https://www.propiedades.com/",
]


def fetch(query, category, limit):
    params = {"q": query, "limit": limit}
    if category:
        params["category"] = CATEGORIES[category]
    url = SEARCH_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise SystemExit(
                "Mercado Libre bloqueo la peticion (HTTP 403). Desde IP residencial funciona; "
                f"como alternativa usa estos portales: {', '.join(PORTALS)}"
            ) from exc
        raise SystemExit(f"La API respondio HTTP {exc.code}.") from exc


def summarize(item):
    attributes = {a.get("id"): a.get("value_name") for a in item.get("attributes") or []}
    price = item.get("price")
    currency = item.get("currency_id")
    if currency == "MXN":
        price = f"${price:,.2f} MXN"
    return {
        "titulo": item.get("title"),
        "precio": price,
        "condicion": item.get("condition"),
        "dormitorios": attributes.get("ROOMS"),
        "banos": attributes.get("BATHROOMS"),
        "superficie_m2": attributes.get("COVERED_AREA"),
        "ubicacion": item.get("address") and item.get("address").get("city_name"),
        "link": item.get("permalink"),
    }


def main():
    parser = argparse.ArgumentParser(description="Busqueda de inmuebles en Mexico")
    parser.add_argument("--q", required=True, help="Busqueda (ej. 'departamento polanco')")
    parser.add_argument("--tipo", choices=["venta", "renta"], default="venta")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    data = fetch(args.q, args.tipo, args.limit)
    items = data.get("results") or []
    if not items:
        raise SystemExit("No se encontraron inmuebles para esa busqueda.")

    print(json.dumps(
        {
            "source": "api.mercadolibre.com (MLM Inmuebles)",
            "query": args.q,
            "tipo": args.tipo,
            "total": data.get("paging", {}).get("total"),
            "results": [summarize(item) for item in items],
            "portales_alternativos": PORTALS,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
