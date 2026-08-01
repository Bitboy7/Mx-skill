#!/usr/bin/env python3
"""Clima en ciudades de Mexico.

Fuente publica: Open-Meteo (forecast + geocodificacion), sin API key.
Referencia oficial de Mexico: Servicio Meteorologico Nacional (CONAGUA/SMN).

Uso:
  python3 mx_weather.py --place "Guadalajara"
  python3 mx_weather.py --place "Monterrey" --days 3
  python3 mx_weather.py --lat 19.43 --lon -99.13 --days 5
"""

import argparse
import json
import urllib.parse
import urllib.request

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
USER_AGENT = "k-skill-mx-weather/1.0 (+https://github.com/NomaDamas/k-skill)"

WMO_CODES = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna",
    55: "Llovizna densa",
    61: "Lluvia ligera",
    63: "Lluvia",
    65: "Lluvia fuerte",
    71: "Nieve ligera",
    73: "Nieve",
    75: "Nieve fuerte",
    80: "Chubascos ligeros",
    81: "Chubascos",
    82: "Chubascos violentos",
    95: "Tormenta",
    96: "Tormenta con granizo",
    99: "Tormenta con granizo fuerte",
}


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def geocode(place):
    url = GEOCODE_URL + "?" + urllib.parse.urlencode(
        {"name": place, "count": 5, "language": "es", "countryCode": "MX"}
    )
    results = (http_get_json(url).get("results") or [])
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


def fetch_forecast(lat, lon, days):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": days,
    }
    url = FORECAST_URL + "?" + urllib.parse.urlencode(params)
    return http_get_json(url)


def main():
    parser = argparse.ArgumentParser(description="Clima en ciudades de Mexico (Open-Meteo)")
    parser.add_argument("--place", help="Ciudad o localidad en Mexico")
    parser.add_argument("--lat", type=float, help="Latitud (alternativa a --place)")
    parser.add_argument("--lon", type=float, help="Longitud (alternativa a --place)")
    parser.add_argument("--days", type=int, default=3, help="Dias de pronostico (max 7)")
    args = parser.parse_args()

    if not 1 <= args.days <= 7:
        parser.error("--days debe estar entre 1 y 7")

    if args.lat is not None and args.lon is not None:
        anchor = {"query": "coordenadas", "latitude": args.lat, "longitude": args.lon}
    elif args.place:
        anchor = geocode(args.place)
    else:
        parser.error("Proporciona --place o --lat/--lon.")
    forecast = fetch_forecast(anchor["latitude"], anchor["longitude"], args.days)

    current = forecast.get("current") or {}
    daily = forecast.get("daily") or {}

    days_out = []
    dates = daily.get("time") or []
    for i, date in enumerate(dates):
        code = (daily.get("weather_code") or [None])[i]
        days_out.append(
            {
                "fecha": date,
                "max_c": (daily.get("temperature_2m_max") or [None])[i],
                "min_c": (daily.get("temperature_2m_min") or [None])[i],
                "prob_lluvia_pct": (daily.get("precipitation_probability_max") or [None])[i],
                "descripcion": WMO_CODES.get(code, "N/A"),
            }
        )

    print(json.dumps(
        {
            "source": "Open-Meteo (referencia oficial: CONAGUA/SMN)",
            "place": anchor,
            "actual": {
                "temp_c": current.get("temperature_2m"),
                "humedad_pct": current.get("relative_humidity_2m"),
                "viento_kmh": current.get("wind_speed_10m"),
                "descripcion": WMO_CODES.get(current.get("weather_code"), "N/A"),
            },
            "pronostico": days_out,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
