#!/usr/bin/env python3
"""Consulta los resultados oficiales de la Lotería Nacional de Mexico.

Fuente oficial: https://www.loterianacional.gob.mx/Home/Resultados
La pagina renderiza en el HTML los paneles con los resultados mas recientes de
cada juego (Melate, Revancha, Revanchita, Chispazo, Tris, Progol, etc.).

Uso:
  python3 melate_results.py latest
  python3 melate_results.py --game melate
  python3 melate_results.py check --numbers "6 14 21 32 40 49"
"""

import argparse
import html
import json
import re
import sys
import urllib.request

RESULTADOS_URL = "https://www.loterianacional.gob.mx/Home/Resultados"
BOLETO_URL = "https://www.loterianacional.gob.mx/Home/BuscadorBoleto"
USER_AGENT = "k-skill-melate-results/1.0 (+https://github.com/NomaDamas/k-skill)"

GAME_NAMES = {
    "Melates": "Melate",
    "MelateRetro": "Melate Retro",
    "Tris": "Tris",
    "Chispazo": "Chispazo",
    "GanaGato": "Gana Gato",
    "Progol": "Progol",
    "ProgolMS": "Progol Marcador",
    "Protouch": "Protouch",
    "Mayor": "Mayor",
    "Superior": "Superior",
    "Magno": "Magno",
    "Zodiaco": "Zodiaco",
    "ZodiacoEspecial": "Zodiaco Especial",
    "Especial": "Especial",
    "Gordito": "Gordito",
}


def fetch_page():
    req = urllib.request.Request(RESULTADOS_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def split_panels(page):
    text = html.unescape(page)
    panels = []
    for m in re.finditer(r'id="pnlResul([A-Za-z0-9]+)"[^>]*>(.*?)(?=<div id="pnlResul|\Z)', text, re.S):
        panels.append((m.group(1), m.group(2)))
    return panels


def parse_panel(game_key, body):
    numbers = []
    for nm in re.finditer(r"N[uú]mero ganador[^<]*</p>\s*<p[^>]*>([^<]+)</p>", body):
        label = nm.group(0)
        label_match = re.search(r"N[uú]mero ganador\s*([^<]*)", label)
        numbers.append(
            {
                "label": (label_match.group(1).strip() or GAME_NAMES.get(game_key, game_key)),
                "numbers": " ".join(nm.group(1).split()),
            }
        )

    def field(header):
        m = re.search(rf"{header}</p>\s*<p[^>]*>([^<]+)</p>", body, re.I)
        return " ".join(m.group(1).split()) if m else None

    bolsa = re.search(r"Bolsa acumulada[^<]*</p>\s*<p[^>]*>([^<]+)</p>", body)
    return {
        "game": GAME_NAMES.get(game_key, game_key),
        "sorteo": field("Sorteo"),
        "draw_date": field("Fecha"),
        "entries": numbers,
        "bolsa_acumulada_millones": " ".join(bolsa.group(1).split()) if bolsa else None,
    }


def latest(only_game=None):
    page = fetch_page()
    results = []
    for game_key, body in split_panels(page):
        panel = parse_panel(game_key, body)
        if not panel["entries"] and not panel["sorteo"]:
            continue
        if only_game and panel["game"].lower() != only_game.lower():
            continue
        results.append(panel)
    if not results:
        raise SystemExit("No se encontraron resultados en la pagina oficial.")
    return results


def check_numbers(numbers):
    melate = None
    for panel in latest():
        if panel["game"] == "Melate":
            melate = panel
            break
    if melate is None:
        raise SystemExit("No se encontro el panel de Melate en la pagina oficial.")

    main_entry = next(
        (e for e in melate["entries"] if "revancha" not in e["label"].lower() and "revanchita" not in e["label"].lower()),
        melate["entries"][0],
    )
    draw_numbers = {int(n) for n in main_entry["numbers"].split("-")[0].split() if n.isdigit()}
    user_numbers = [int(n) for n in numbers if n.isdigit()]
    matches = sorted(set(n for n in user_numbers if n in draw_numbers))

    return {
        "game": "Melate",
        "sorteo": melate["sorteo"],
        "draw_date": melate["draw_date"],
        "draw_numbers": main_entry["numbers"],
        "user_numbers": user_numbers,
        "matching_numbers": matches,
        "match_count": len(matches),
        "official_checker": BOLETO_URL,
    }


def build_parser():
    parser = argparse.ArgumentParser(description="Resultados oficiales de la Lotería Nacional de México")
    sub = parser.add_subparsers(dest="command")

    p_latest = sub.add_parser("latest", help="Resultados mas recientes de todos los juegos")
    p_latest.add_argument("--game", help="Filtrar por juego (melate, revancha, chispazo, tris, ...)")

    p_check = sub.add_parser("check", help="Comparar tus numeros contra el ultimo sorteo de Melate")
    p_check.add_argument("--numbers", required=True, help="Seis numeros separados por espacios")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "latest"

    if command == "latest":
        result = {"source": RESULTADOS_URL, "results": latest(args.game)}
    elif command == "check":
        result = check_numbers(args.numbers.split())
    else:
        parser.error(f"comando desconocido: {command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
