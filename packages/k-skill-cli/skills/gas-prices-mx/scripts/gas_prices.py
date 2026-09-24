#!/usr/bin/env python3
"""Gasolineras mas baratas cerca de una ubicacion en Mexico.

Fuente oficial de precios: publicacion de la CRE (Comision Reguladora de
Energia):
  https://publicacionexterna.azurewebsites.net/publicaciones/places   (catalogo)
  https://publicacionexterna.azurewebsites.net/publicaciones/prices   (precios)
Ambos endpoints son publicos (XML, sin API key). La antigua API
`api.datos.gob.mx/v1/precio.gasolina.publico` fue retirada. Geocodificacion
publica via Open-Meteo.

Uso:
  python3 gas_prices.py --place "Cuauhtemoc, Ciudad de Mexico"
  python3 gas_prices.py --lat 19.4326 --lon -99.1332 --fuel premium --radius-km 15
"""

import argparse
import json
import math
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

PLACES_URL = "https://publicacionexterna.azurewebsites.net/publicaciones/places"
PRICES_URL = "https://publicacionexterna.azurewebsites.net/publicaciones/prices"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

FUELS = ("regular", "premium", "diesel")


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/xml,text/xml,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"La publicacion de precios de la CRE respondio HTTP {exc.code}. "
            "Reintenta en unos minutos o consulta el portal oficial de la CRE."
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo contactar la publicacion de precios de la CRE: {exc.reason}") from exc


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"El geocodificador respondio HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo contactar el geocodificador: {exc.reason}") from exc


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


def parse_places(xml_bytes):
    root = ET.fromstring(xml_bytes)
    places = {}
    for node in root.findall("place"):
        place_id = node.get("place_id")
        if not place_id:
            continue
        location = node.find("location")
        lat = lon = None
        if location is not None:
            lat = _to_float(location.findtext("y"))
            lon = _to_float(location.findtext("x"))
        places[place_id] = {
            "nombre": (node.findtext("name") or "").strip() or None,
            "cre_id": (node.findtext("cre_id") or "").strip() or None,
            "latitud": lat,
            "longitud": lon,
        }
    return places


def parse_prices(xml_bytes):
    root = ET.fromstring(xml_bytes)
    prices = {}
    for node in root.findall("place"):
        place_id = node.get("place_id")
        if not place_id:
            continue
        record = {}
        for price in node.findall("gas_price"):
            fuel = price.get("type")
            value = _to_float(price.text)
            if fuel and value is not None:
                record[fuel] = value
        if record:
            prices[place_id] = record
    return prices


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0088
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.asin(math.sqrt(a))


def load_stations():
    places = parse_places(http_get(PLACES_URL))
    prices = parse_prices(http_get(PRICES_URL))
    stations = []
    for place_id, info in places.items():
        record = prices.get(place_id)
        if not record or info["latitud"] is None or info["longitud"] is None:
            continue
        stations.append({"place_id": place_id, **info, "precios": record})
    return stations


def summarize(station, fuel):
    lat = station["latitud"]
    lon = station["longitud"]
    return {
        "nombre": station.get("nombre"),
        "razon_social": station.get("nombre"),
        "cre_id": station.get("cre_id"),
        "latitud": lat,
        "longitud": lon,
        "precio": station["precios"].get(fuel),
        "precios": {k: station["precios"].get(k) for k in FUELS if k in station["precios"]},
        "mapa": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
    }


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(description="Gasolineras mas baratas cerca de una ubicacion en Mexico")
    parser.add_argument("--place", help="Nombre de la ubicacion (colonia, ciudad, estado)")
    parser.add_argument("--lat", type=float, help="Latitud (alternativa a --place)")
    parser.add_argument("--lon", type=float, help="Longitud (alternativa a --place)")
    parser.add_argument("--fuel", choices=FUELS, default="regular")
    parser.add_argument("--radius-km", type=float, default=10.0)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)

    if args.lat is not None and args.lon is not None:
        anchor = {"query": "coordenadas", "latitude": args.lat, "longitude": args.lon}
    elif args.place:
        anchor = geocode(args.place)
    else:
        parser.error("Proporciona --place o --lat/--lon.")

    stations = load_stations()
    if not stations:
        raise SystemExit("La publicacion de la CRE devolvio un catalogo vacio.")

    candidates = []
    for station in stations:
        price = station["precios"].get(args.fuel)
        if price is None:
            continue
        distance = haversine_km(anchor["latitude"], anchor["longitude"], station["latitud"], station["longitud"])
        if distance > args.radius_km:
            continue
        item = summarize(station, args.fuel)
        item["distancia_km"] = round(distance, 2)
        candidates.append(item)

    candidates.sort(key=lambda item: item["precio"])

    print(json.dumps(
        {
            "source": PRICES_URL,
            "catalogo": PLACES_URL,
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
