#!/usr/bin/env python3
"""Banos publicos cerca de una ubicacion en Mexico.

Fuente publica: OpenStreetMap via Overpass API (sin API key, datos ODbL).
La ubicacion se geocodifica con la API publica de Open-Meteo.

Uso:
  python3 mx_restroom_nearby.py --place "Zocalo CDMX"
  python3 mx_restroom_nearby.py --place "Roma Norte" --radius 1200 --limit 5
  python3 mx_restroom_nearby.py --lat 19.4326 --lon -99.1332 --json
"""

import argparse
import json
import math
import time
import urllib.parse
import urllib.request

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
USER_AGENT = "k-skill-mx-restroom-nearby/1.0 (+https://github.com/NomaDamas/k-skill)"

ACCESS_LABELS = {
    "yes": "Publico",
    "public": "Publico",
    "permissive": "Publico",
    "customers": "Solo clientes",
    "private": "Privado",
    "no": "Privado",
}


def http_get_json(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _geocode_results(place, country_code=None):
    params = {"name": place, "count": 5, "language": "es"}
    if country_code:
        params["countryCode"] = country_code
    url = GEOCODE_URL + "?" + urllib.parse.urlencode(params)
    return http_get_json(url).get("results") or []


def geocode(place):
    results = _geocode_results(place, "MX")
    if not results:
        fallback = _geocode_results(place)
        results = [item for item in fallback if item.get("country_code") == "MX"] or fallback
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


def build_overpass_query(lat, lon, radius):
    return (
        "[out:json][timeout:25];"
        f'nwr["amenity"="toilets"](around:{int(radius)},{lat},{lon});'
        "out center tags;"
    )


def overpass_url(endpoint, query):
    return endpoint + "?" + urllib.parse.urlencode({"data": query})


def fetch_overpass(query, endpoints=None, attempts=2, pause=1.5):
    """Consulta Overpass probando endpoints en orden y reintentando si todo falla."""
    endpoints = endpoints or OVERPASS_ENDPOINTS
    last_error = None
    for attempt in range(max(1, attempts)):
        for endpoint in endpoints:
            try:
                return http_get_json(overpass_url(endpoint, query))
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        if attempt + 1 < attempts:
            time.sleep(pause)
    raise SystemExit(f"No se pudo consultar OpenStreetMap/Overpass: {last_error}")


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(a)))


def element_coords(element):
    if element.get("lat") is not None and element.get("lon") is not None:
        return element["lat"], element["lon"]
    center = element.get("center") or {}
    if center.get("lat") is not None and center.get("lon") is not None:
        return center["lat"], center["lon"]
    return None, None


def classify_fee(tags):
    fee = (tags.get("fee") or "").lower()
    if fee in ("no", "free", "0"):
        return "Gratis"
    if fee in ("yes", "paid", "1"):
        return "De pago"
    return "No especificado"


def classify_access(tags):
    access = (tags.get("access") or "").lower()
    return ACCESS_LABELS.get(access, "No especificado")


def format_address(tags):
    if tags.get("addr:full"):
        return tags["addr:full"]
    street = " ".join(part for part in [tags.get("addr:street"), tags.get("addr:housenumber")] if part)
    locality = tags.get("addr:suburb") or tags.get("addr:city")
    parts = [p for p in (street, locality, tags.get("addr:postcode")) if p]
    return ", ".join(parts) if parts else None


def normalize_element(element, lat, lon):
    el_lat, el_lon = element_coords(element)
    if el_lat is None:
        return None
    tags = element.get("tags") or {}
    osm_type = element.get("type") or "node"
    osm_id = element.get("id")
    distance = haversine_km(lat, lon, el_lat, el_lon)
    return {
        "nombre": tags.get("name") or "Bano publico",
        "distancia_km": round(distance, 3),
        "lat": el_lat,
        "lon": el_lon,
        "direccion": format_address(tags),
        "costo": classify_fee(tags),
        "acceso": classify_access(tags),
        "horario": tags.get("opening_hours"),
        "accesible_silla_ruedas": tags.get("wheelchair") == "yes",
        "osm": f"{osm_type}/{osm_id}",
        "mapa": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
    }


def select_results(payload, lat, lon, limit):
    results = []
    for element in payload.get("elements") or []:
        normalized = normalize_element(element, lat, lon)
        if normalized is not None:
            results.append(normalized)
    results.sort(key=lambda row: row["distancia_km"])
    if limit and limit > 0:
        results = results[:limit]
    return results


def build_payload(anchor, radius, results):
    return {
        "source": "OpenStreetMap via Overpass API (c) OpenStreetMap contributors, ODbL",
        "place": anchor,
        "radio_m": int(radius),
        "results": results,
    }


def format_text(payload):
    place = payload.get("place") or {}
    place_name = place.get("name") or place.get("query") or "tu ubicacion"
    results = payload.get("results") or []
    if not results:
        return f"No se encontraron banos publicos cerca de {place_name} en {payload.get('radio_m')} m."
    lines = [f"Banos publicos cerca de {place_name} (radio {payload.get('radio_m')} m):"]
    for row in results:
        details = [row["costo"], row["acceso"]]
        if row.get("horario"):
            details.append(row["horario"])
        lines.append(
            f"• {row['nombre']} — {row['distancia_km']} km ({', '.join(details)})\n  {row['mapa']}"
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Banos publicos cerca (OpenStreetMap/Overpass)")
    parser.add_argument("--place", help="Lugar de referencia en Mexico")
    parser.add_argument("--lat", type=float, help="Latitud (alternativa a --place)")
    parser.add_argument("--lon", type=float, help="Longitud (alternativa a --place)")
    parser.add_argument("--radius", type=int, default=1000, help="Radio de busqueda en metros (por defecto 1000)")
    parser.add_argument("--limit", type=int, default=5, help="Numero maximo de resultados (por defecto 5)")
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args(argv)

    if not 50 <= args.radius <= 10000:
        parser.error("--radius debe estar entre 50 y 10000 metros")

    if args.lat is not None and args.lon is not None:
        anchor = {"query": "coordenadas", "latitude": args.lat, "longitude": args.lon}
    elif args.place:
        anchor = geocode(args.place)
    else:
        parser.error("Proporciona --place o --lat/--lon.")

    query = build_overpass_query(anchor["latitude"], anchor["longitude"], args.radius)
    payload = fetch_overpass(query)
    results = select_results(payload, anchor["latitude"], anchor["longitude"], args.limit)
    response = build_payload(anchor, args.radius, results)

    if args.json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print(format_text(response))


if __name__ == "__main__":
    main()
