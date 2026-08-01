#!/usr/bin/env python3
"""Ecobici CDMX: estaciones con bicicletas disponibles cerca de una ubicacion.

Fuente publica: feed GBFS oficial de Ecobici (gbfs.mex.lyftbikes.com), sin API key.

Uso:
  python3 ecobici_cdmx.py --place "Roma Norte, Ciudad de Mexico"
  python3 ecobici_cdmx.py --lat 19.4194 --lon -99.1600 --limit 5
"""

import argparse
import json
import math
import urllib.parse
import urllib.request

STATION_INFO_URL = "https://gbfs.mex.lyftbikes.com/gbfs/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.mex.lyftbikes.com/gbfs/en/station_status.json"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
USER_AGENT = "k-skill-ecobici-cdmx/1.0 (+https://github.com/NomaDamas/k-skill)"


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0088
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return radius * 2 * math.asin(math.sqrt(a))


def geocode(place):
    candidates = [place, f"{place}, Ciudad de Mexico"]
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        url = GEOCODE_URL + "?" + urllib.parse.urlencode(
            {"name": candidate, "count": 5, "language": "es", "countryCode": "MX"}
        )
        results = (http_get_json(url).get("results") or [])
        for r in results:
            admin = (r.get("admin1") or "").lower()
            if "ciudad de m" in admin:
                return {"query": place, "name": r.get("name"), "admin1": r.get("admin1"),
                        "latitude": r.get("latitude"), "longitude": r.get("longitude")}
    raise SystemExit(
        f"No se encontro {place!r} en Ciudad de Mexico. Usa una colonia conocida o coordenadas --lat/--lon."
    )


def main():
    parser = argparse.ArgumentParser(description="Ecobici CDMX: bicis disponibles cerca")
    parser.add_argument("--place", help="Colonia o punto de referencia en CDMX")
    parser.add_argument("--lat", type=float, help="Latitud (alternativa a --place)")
    parser.add_argument("--lon", type=float, help="Longitud (alternativa a --place)")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--radius-km", type=float, default=3.0)
    args = parser.parse_args()

    if args.lat is not None and args.lon is not None:
        anchor = {"query": "coordenadas", "latitude": args.lat, "longitude": args.lon}
    elif args.place:
        anchor = geocode(args.place)
    else:
        parser.error("Proporciona --place o --lat/--lon.")

    info = http_get_json(STATION_INFO_URL)["data"]["stations"]
    status = http_get_json(STATION_STATUS_URL)["data"]["stations"]
    status_map = {s["station_id"]: s for s in status}

    candidates = []
    for station in info:
        live = status_map.get(station["station_id"])
        if not live:
            continue
        distance = haversine_km(anchor["latitude"], anchor["longitude"], station["lat"], station["lon"])
        if distance > args.radius_km:
            continue
        candidates.append(
            {
                "estacion": station["name"],
                "distancia_km": round(distance, 2),
                "bicis_disponibles": live.get("num_bikes_available", 0),
                "espacios_libres": live.get("num_docks_available", 0),
                "capacidad": station.get("capacity"),
                "activa": bool(live.get("is_installed") and live.get("is_renting")),
            }
        )

    candidates.sort(key=lambda c: c["distancia_km"])

    print(json.dumps(
        {
            "source": "GBFS Ecobici (gbfs.mex.lyftbikes.com)",
            "anchor": anchor,
            "radius_km": args.radius_km,
            "stations_in_range": len(candidates),
            "results": candidates[: args.limit],
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
