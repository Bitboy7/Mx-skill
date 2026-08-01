#!/usr/bin/env python3
"""Precios de la canasta basica en Mexico (PROFECO / datos.gob.mx).

Fuente oficial: dataset "Precios de la canasta basica" de PROFECO publicado en
datos.gob.mx. API publica sin clave. Puede estar temporalmente fuera de servicio
(503) como otras APIs de datos.gob.mx; en ese caso se remite al portal
"Quien es Quien en los Precios" de PROFECO.

Uso:
  python3 precios_canasta.py --top 10
  python3 precios_canasta.py --estado "Jalisco"
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

API_URL = "https://api.datos.gob.mx/v1/precio.canasta.basica"
USER_AGENT = "k-skill-precios-canasta/1.0 (+https://github.com/NomaDamas/k-skill)"
PROFECO_PORTAL = "https://www.profeco.gob.mx/precios/canasta/home.aspx"


def fetch(page_size=100, page=1):
    url = API_URL + "?" + urllib.parse.urlencode({"pageSize": page_size, "page": page})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"La API de canasta basica respondio HTTP {exc.code}. "
            f"Reintenta o consulta el portal de PROFECO: {PROFECO_PORTAL}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo contactar la API: {exc.reason}") from exc


def main():
    parser = argparse.ArgumentParser(description="Precios de la canasta basica en Mexico (PROFECO)")
    parser.add_argument("--top", type=int, default=10, help="Mostrar las N canastas mas baratas")
    parser.add_argument("--estado", help="Filtrar por estado")
    args = parser.parse_args()

    data = fetch()
    items = data.get("results") or []

    if args.estado:
        estado_l = args.estado.lower()
        items = [i for i in items if (i.get("Estado") or i.get("estado") or "").lower() == estado_l]

    items.sort(key=lambda i: float(i.get("CostoCanastaBasica") or i.get("costo") or 0))

    summary = []
    for item in items[: args.top]:
        summary.append(
            {
                "tienda": item.get("NombreTienda") or item.get("tienda"),
                "estado": item.get("Estado") or item.get("estado"),
                "region": item.get("Region") or item.get("region"),
                "costo_mxn": item.get("CostoCanastaBasica") or item.get("costo"),
                "fecha": item.get("Fecha") or item.get("fecha"),
            }
        )

    print(json.dumps(
        {
            "source": "PROFECO canasta basica (datos.gob.mx)",
            "filter": args.estado,
            "total": len(items),
            "results": summary,
            "portal": PROFECO_PORTAL,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
