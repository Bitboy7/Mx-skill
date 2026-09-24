#!/usr/bin/env python3
"""Calidad del aire en ciudades de Mexico.

Fuente publica: Open-Meteo Air Quality API (PM10, PM2.5, US AQI), sin API key.
Referencia oficial de Mexico: SEDEMA / Sistema de Monitoreo Atmosferico
(aire.cdmx.gob.mx) y SEMARNAT.

Uso:
  python3 mx_air_quality.py --place "Ciudad de Mexico"
  python3 mx_air_quality.py --place "Monterrey" --json
  python3 mx_air_quality.py --lat 19.43 --lon -99.13
"""

import argparse
import json
import urllib.parse
import urllib.request

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
USER_AGENT = "k-skill-mx-air-quality/1.0 (+https://github.com/NomaDamas/k-skill)"

# Campos actuales que se solicitan al upstream.
CURRENT_FIELDS = "pm10,pm2_5,us_aqi,carbon_monoxide,nitrogen_dioxide,ozone,sulphur_dioxide"

# Cortes US EPA para el indice US AQI.
US_AQI_BREAKPOINTS = [
    (50, "Buena", "Sin riesgo. Disfruta las actividades al aire libre."),
    (100, "Moderada", "Aceptable; las personas muy sensibles pueden notar molestias."),
    (150, "Danina para grupos sensibles", "Grupos sensibles: reduce el esfuerzo prolongado al aire libre."),
    (200, "Danina", "Todos pueden sentir efectos; limita el esfuerzo al aire libre."),
    (300, "Muy danina", "Alerta sanitaria: evita actividades al aire libre."),
    (10 ** 9, "Peligrosa", "Emergencia sanitaria: permanece en interiores."),
]


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def classify_us_aqi(value):
    """Devuelve (categoria, recomendacion) para un valor US AQI."""
    if value is None:
        return ("Sin dato", "No hay indice disponible para esta ubicacion.")
    for limit, category, advice in US_AQI_BREAKPOINTS:
        if value <= limit:
            return (category, advice)
    return (US_AQI_BREAKPOINTS[-1][1], US_AQI_BREAKPOINTS[-1][2])


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


def fetch_air_quality(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": CURRENT_FIELDS,
        "timezone": "auto",
    }
    url = AIR_QUALITY_URL + "?" + urllib.parse.urlencode(params)
    return http_get_json(url)


def build_payload(anchor, data):
    current = data.get("current") or {}
    us_aqi = current.get("us_aqi")
    category, advice = classify_us_aqi(us_aqi)
    return {
        "source": "Open-Meteo Air Quality (referencia oficial: SEDEMA / SEMARNAT)",
        "place": anchor,
        "medido_en": current.get("time"),
        "calidad": {
            "indice_us_aqi": us_aqi,
            "categoria": category,
            "recomendacion": advice,
            "pm10_ug_m3": current.get("pm10"),
            "pm2_5_ug_m3": current.get("pm2_5"),
            "monoxido_carbono_ug_m3": current.get("carbon_monoxide"),
            "dioxido_nitrogeno_ug_m3": current.get("nitrogen_dioxide"),
            "ozono_ug_m3": current.get("ozone"),
            "dioxido_azufre_ug_m3": current.get("sulphur_dioxide"),
        },
    }


def format_text(payload):
    place = payload.get("place") or {}
    quality = payload.get("calidad") or {}
    place_name = place.get("name") or place.get("query") or "tu ubicacion"
    lines = [
        f"Calidad del aire en {place_name}",
        f"Indice US AQI: {quality.get('indice_us_aqi')} ({quality.get('categoria')})",
        f"PM2.5: {quality.get('pm2_5_ug_m3')} ug/m3",
        f"PM10: {quality.get('pm10_ug_m3')} ug/m3",
        f"Medido: {payload.get('medido_en')}",
        "",
        quality.get("recomendacion") or "",
    ]
    return "\n".join(lines).strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calidad del aire en Mexico (Open-Meteo)")
    parser.add_argument("--place", help="Ciudad o localidad en Mexico")
    parser.add_argument("--lat", type=float, help="Latitud (alternativa a --place)")
    parser.add_argument("--lon", type=float, help="Longitud (alternativa a --place)")
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args(argv)

    if args.lat is not None and args.lon is not None:
        anchor = {"query": "coordenadas", "latitude": args.lat, "longitude": args.lon}
    elif args.place:
        anchor = geocode(args.place)
    else:
        parser.error("Proporciona --place o --lat/--lon.")

    data = fetch_air_quality(anchor["latitude"], anchor["longitude"])
    payload = build_payload(anchor, data)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))


if __name__ == "__main__":
    main()
