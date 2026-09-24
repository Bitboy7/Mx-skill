#!/usr/bin/env python3
"""Dias feriados oficiales de Mexico.

Fuente publica: Nager.Date (https://date.nager.at), sin API key.
Los datos de dias feriados de Mexico provienen del calendario oficial
(Ley Federal del Trabajo) agregado por Nager.Date.

Uso:
  python3 mx_holidays.py
  python3 mx_holidays.py --year 2027 --json
  python3 mx_holidays.py --next
"""

import argparse
import datetime as dt
import json
import urllib.request

BASE_URL = "https://date.nager.at/api/v3"
USER_AGENT = "k-skill-mx-holidays/1.0 (+https://github.com/NomaDamas/k-skill)"

TYPE_LABELS = {
    "Public": "Oficial",
    "Bank": "Bancario",
    "School": "Escolar",
    "Authorities": "Autoridades",
    "Optional": "Opcional",
    "Observance": "Conmemorativo",
}


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_holidays(year):
    return http_get_json(f"{BASE_URL}/PublicHolidays/{year}/MX")


def fetch_next_holidays():
    return http_get_json(f"{BASE_URL}/NextPublicHolidays/MX")


def parse_date(value):
    return dt.date.fromisoformat(value)


def days_until(value, today=None):
    today = today or dt.date.today()
    return (parse_date(value) - today).days


def translate_type(type_name):
    return TYPE_LABELS.get(type_name, type_name)


def normalize(items, today=None):
    today = today or dt.date.today()
    normalized = []
    for item in items:
        date_value = item.get("date")
        if not date_value:
            continue
        try:
            delta = days_until(date_value, today)
        except ValueError:
            delta = None
        normalized.append(
            {
                "fecha": date_value,
                "nombre": item.get("name") or item.get("localName"),
                "nombre_local": item.get("localName") or item.get("name"),
                "tipos": [translate_type(t) for t in (item.get("types") or [])],
                "dias_faltantes": delta,
            }
        )
    normalized.sort(key=lambda row: row["fecha"])
    return normalized


def build_payload(items, mode, year=None, today=None):
    today = today or dt.date.today()
    return {
        "source": "Nager.Date (calendario oficial de dias feriados de Mexico)",
        "modo": mode,
        "year": year,
        "today": today.isoformat(),
        "results": normalize(items, today),
    }


def format_text(payload):
    label = "Proximos dias feriados" if payload["modo"] == "next" else f"Dias feriados {payload.get('year')}"
    lines = [f"{label}:"]
    for row in payload["results"]:
        types = ", ".join(row["tipos"]) or "Oficial"
        suffix = ""
        if row["dias_faltantes"] is not None and row["dias_faltantes"] >= 0:
            suffix = f" (en {row['dias_faltantes']} dias)"
        lines.append(f"• {row['fecha']} — {row['nombre_local']} [{types}]{suffix}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Dias feriados de Mexico (Nager.Date)")
    parser.add_argument("--year", type=int, default=None, help="Anio (por defecto el actual)")
    parser.add_argument("--next", action="store_true", help="Solo los proximos dias feriados")
    parser.add_argument("--json", action="store_true", help="Salida JSON cruda")
    args = parser.parse_args(argv)

    if args.next:
        items = fetch_next_holidays()
        payload = build_payload(items, mode="next")
    else:
        year = args.year or dt.date.today().year
        items = fetch_holidays(year)
        payload = build_payload(items, mode="year", year=year)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(payload))


if __name__ == "__main__":
    main()
