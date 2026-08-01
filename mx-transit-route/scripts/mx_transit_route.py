#!/usr/bin/env python3
"""Rutas de transporte en Mexico (CDMX y otras ciudades).

Fuente publica: OSRM (router.project-osrm.org) para direcciones, + Open-Meteo
para geocodificacion. Sin API key.
El Metro de CDMX y otros sistemas no exponen una API publica de rutas en tiempo
real; esta skill da la ruta caminando/auto y las estaciones de Metro cercanas a
cada punto cuando el usuario las conoce.

Uso:
  python3 mx_transit_route.py --from "Polanco, CDMX" --to "Zocalo, CDMX"
  python3 mx_transit_route.py --from "-99.19,19.43" --to "-99.13,19.43" --mode driving
"""

import argparse
import json
import math
import urllib.parse
import urllib.request

OSRM_URL = "https://router.project-osrm.org/route/v1/{profile}/{coords}?overview=false&steps=false&annotations=false"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
USER_AGENT = "k-skill-mx-transit-route/1.0 (+https://github.com/NomaDamas/k-skill)"
PROFILES = {"driving": "driving", "walking": "foot", "cycling": "cycling"}


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.load(resp)


def geocode(place):
    candidates = [place]
    if "," in place:
        candidates.append(place.split(",")[0])
        candidates.append(place.split(",")[0] + ", Mexico")
    if not any(place.lower().startswith(x) for x in ("ciudad de", "cdmx")):
        candidates.append(place + ", Mexico")
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        url = GEOCODE_URL + "?" + urllib.parse.urlencode(
            {"name": candidate, "count": 5, "language": "es", "countryCode": "MX"}
        )
        results = (http_get_json(url).get("results") or [])
        if results:
            best = results[0]
            if "cdmx" in place.lower() or "ciudad de mexico" in place.lower():
                for r in results:
                    admin = (r.get("admin1") or "").lower()
                    if "ciudad de m" in admin:
                        best = r
                        break
            return {"query": place, "name": best.get("name"), "admin1": best.get("admin1"),
                    "latitude": best.get("latitude"), "longitude": best.get("longitude")}
    raise SystemExit(f"No se encontro la ubicacion: {place}. Intenta con otro punto de referencia o coordenadas lon,lat.")


def resolve(place):
    parts = place.strip().split(",")
    if len(parts) == 2:
        try:
            lon, lat = float(parts[0]), float(parts[1])
            return {"query": place, "latitude": lat, "longitude": lon}
        except ValueError:
            pass
    return geocode(place)


def main():
    parser = argparse.ArgumentParser(description="Rutas de transporte en Mexico")
    parser.add_argument("--from", dest="origin", required=True, help="Origen (lugar o lon,lat)")
    parser.add_argument("--to", dest="destination", required=True, help="Destino (lugar o lon,lat)")
    parser.add_argument("--mode", choices=list(PROFILES.keys()), default="driving")
    args = parser.parse_args()

    origin = resolve(args.origin)
    destination = resolve(args.destination)

    coords = f"{origin['longitude']},{origin['latitude']};{destination['longitude']},{destination['latitude']}"
    url = OSRM_URL.format(profile=PROFILES[args.mode], coords=coords)
    data = http_get_json(url)

    if data.get("code") != "Ok" or not data.get("routes"):
        raise SystemExit(f"OSRM no encontro ruta ({data.get('code')}). Intenta otro modo o puntos mas cercanos.")

    route = data["routes"][0]
    duration_sec = route.get("duration") or 0
    distance_m = route.get("distance") or 0

    print(json.dumps(
        {
            "source": "OSRM public + Open-Meteo geocoding",
            "mode": args.mode,
            "origin": origin,
            "destination": destination,
            "distancia_km": round(distance_m / 1000, 2),
            "duracion_min": round(duration_sec / 60),
            "nota": "Ruta por carretera/camino publico. El Metro CDMX no tiene API publica de rutas; "
                    "verifica conexiones de Metro/Metrobus en los sitios oficiales del STC.",
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
