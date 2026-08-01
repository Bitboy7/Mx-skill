#!/usr/bin/env python3
"""Consulta codigos postales de Mexico y sus colonias asociadas.

Fuente publica primaria: api.zippopotam.us/mx (sin API key, respuesta JSON).
La base oficial de referencia es el catalogo SEPOMEX de Correos de Mexico.

Uso:
  python3 mx_zipcode_search.py 06600
  python3 mx_zipcode_search.py 01000 --json
"""

import argparse
import json
import re
import sys
import urllib.request

API_URL = "https://api.zippopotam.us/mx/{cp}"
USER_AGENT = "k-skill-mx-zipcode-search/1.0 (+https://github.com/NomaDamas/k-skill)"
SEPOMEX_REF = "https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/ConsultaCP.aspx"


def fetch_cp(cp):
    url = API_URL.format(cp=cp)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise SystemExit(f"No se encontro el codigo postal {cp} en la fuente publica.")
        raise SystemExit(f"La fuente respondio HTTP {exc.code}. Reintenta o consulta el catalogo SEPOMEX oficial.") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo contactar la fuente: {exc.reason}") from exc


def parse(data):
    places = []
    for place in data.get("places") or []:
        places.append(
            {
                "colonia": place.get("place name"),
                "municipio": place.get("municipality"),
                "estado": place.get("state"),
                "latitud": place.get("latitude"),
                "longitud": place.get("longitude"),
            }
        )
    return {
        "cp": data.get("post code"),
        "pais": data.get("country"),
        "colonia_principal": places[0]["colonia"] if places else None,
        "estado": places[0]["estado"] if places else None,
        "places": places,
        "reference": SEPOMEX_REF,
    }


def main():
    parser = argparse.ArgumentParser(description="Consulta el codigo postal de Mexico y sus colonias")
    parser.add_argument("cp", help="Codigo postal de 5 digitos")
    args = parser.parse_args()

    cp = args.cp.strip()
    if not re.fullmatch(r"\d{5}", cp):
        raise SystemExit("El codigo postal debe tener exactamente 5 digitos.")

    print(json.dumps(parse(fetch_cp(cp)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
