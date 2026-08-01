#!/usr/bin/env python3
"""Gasolineras mas baratas cerca de una ubicacion en Mexico.

Fuente oficial de precios: API publica de la CRE (Comision Reguladora de
Energia) publicada en datos.gob.mx:
  https://api.datos.gob.mx/v1/precio.gasolina.publico
Sin API key. Geocodificacion publica via Open-Meteo.

Uso:
  python3 gas_prices.py --place "Cuauhtemoc, Ciudad de Mexico"
  python3 gas_prices.py --lat 19.4326 --lon -99.1332 --fuel premium --radius-km 15
"""

import argparse
import json
import math
import sys
import urllib.parse
import urllib.request

API_URL = "https://api.datos.gob.mx/v1/precio.gasolina.publico"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
USER_AGENT = "k-skill-gas-prices-mx/1.0 (+https://github.com/NomaDamas/k-skill)"

FUELS = ("regular", "premium", "diesel")


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"La API de precios de gasolina respondio HTTP {exc.code}. "
            "Reintenta en unos minutos o consulta el portal oficial de la CRE."
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo contactar la API de precios: {exc.reason}") from exc


def geocode(place):
    url = GEOCODE_URL + "?" + urllib.parse.urlencode(
        {"name": place, "count": 5, "language": "es", "countryCode": "MX"}
    )
    data = http_get_json(url)
    results = data.get("results") or []
    if not results:
        raise SystemExit(f"No se encontro la ubicacion: {place}")
    best = results[0]
    return {
        "query": place,
        "name": best.get("name"),
        "admin1": best.get("admin1"),
        "latitude": best.get("latitude"),
        "longitude": best.get("longitude"),
    }


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0088
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.asin(math.sqrt(a))


def fetch_stations(max_pages):
    stations = []
    for page in range(1, max_pages + 1):
        url = API_URL + "?" + urllib.parse.urlencode({"page": page, "pageSize": 100})
        data = http_get_json(url)
        items = data.get("results") or []
        stations.extend(items)
        pagination = data.get("pagination") or {}
        total = pagination.get("total")
        if not items or (total is not None and len(stations) >= int(total)):
            break
    return stations


def price_of(station, fuel):
    raw = station.get(fuel)
    if raw is None or raw == "":
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def summarize(station, fuel):
    return {
        "cre_id": station.get("cre_id"),
        "razon_social": station.get("razon_social"),
        "calle": station.get("calle"),
        "colonia": station.get("colonia"),
        "municipio": station.get("municipio"),
        "estado": station.get("estado"),
        "cp": station.get("cp"),
        "latitud": station.get("latitud"),
        "longitud": station.get("longitud"),
        "precio": price_of(station, fuel),
        "fecha_actualizacion": station.get("fecha_actualizacion"),
    }


def main():
    parser = argparse.ArgumentParser(description="Gasolineras mas baratas cerca de una ubicacion en Mexico")
    parser.add_argument("--place", help="Nombre de la ubicacion (colonia, ciudad, estado)")
    parser.add_argument("--lat", type=float, help="Latitud (alternativa a --place)")
    parser.add_argument("--lon", type=float, help="Longitud (alternativa a --place)")
    parser.add_argument("--fuel", choices=FUELS, default="regular")
    parser.add_argument("--radius-km", type=float, default=10.0)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-pages", type=int, default=20, help="Maximo de paginas de 100 estaciones a recorrer")
    args = parser.parse_args()

    if args.lat is not None and args.lon is not None:
        anchor = {"query": "coordenadas", "latitude": args.lat, "longitude": args.lon}
    elif args.place:
        anchor = geocode(args.place)
    else:
        parser.error("Proporciona --place o --lat/--lon.")

    stations = fetch_stations(args.max_pages)
    if not stations:
        raise SystemExit("La API devolvio un catalogo vacio.")

    candidates = []
    for station in stations:
        try:
            lat = float(station.get("latitud"))
            lon = float(station.get("longitud"))
        except (TypeError, ValueError):
            continue
        distance = haversine_km(anchor["latitude"], anchor["longitude"], lat, lon)
        price = price_of(station, args.fuel)
        if price is None or distance > args.radius_km:
            continue
        item = summarize(station, args.fuel)
        item["distancia_km"] = round(distance, 2)
        candidates.append(item)

    candidates.sort(key=lambda item: item["precio"])

    print(json.dumps(
        {
            "source": API_URL,
            "fuel": args.fuel,
            "anchor": anchor,
            "radius_km": args.radius_km,
            "stations_scanned": len(stations),
            "stations_in_range": len(candidates),
            "results": candidates[: args.limit],
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
