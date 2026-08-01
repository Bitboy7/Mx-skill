#!/usr/bin/env python3
"""Cartelera de cines en Mexico: Cinemex (API publica).

Fuente verificada: api.cinemex.com/rest (header X-API-Consumer-Key publico).
Cinepolis no expone un API publico estable; su portal cinepolis.com/cartelera
sigue siendo la superficie oficial para funciones Cinepolis.

Uso:
  python3 cine_mx.py movies
  python3 cine_mx.py movies --area 1
  python3 cine_mx.py functions --cinema 1 --movie 71994
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "https://api.cinemex.com/rest/v2.37.2"
CONSUMER_KEY = "XXQha7vz4kdvoMSdixhN"
USER_AGENT = "k-skill-cine-mx/1.0 (+https://github.com/NomaDamas/k-skill)"
CINEPOLIS_PORTAL = "https://www.cinepolis.com/cartelera"


def http_get_json(path):
    url = API_BASE + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "X-API-Consumer-Key": CONSUMER_KEY,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"La API de Cinemex respondio HTTP {exc.code}.") from exc


def summarize_movie(movie):
    info = movie.get("info") or {}
    return {
        "id": movie.get("id"),
        "titulo": movie.get("name"),
        "genero": info.get("genre"),
        "duracion_min": info.get("duration"),
        "sinopsis": (info.get("sinopsis") or "")[:180] or None,
    }


def summarize_function(func):
    return {
        "id": func.get("id"),
        "fecha": func.get("datetime"),
        "pantalla": func.get("screen_number"),
        "sala": func.get("auditorium_name"),
        "disponibilidad": func.get("availability"),
        "link_checkout": func.get("url_checkout"),
    }


def main():
    parser = argparse.ArgumentParser(description="Cartelera de cines en Mexico (Cinemex)")
    sub = parser.add_subparsers(dest="command")

    p_movies = sub.add_parser("movies", help="Cartelera actual")
    p_movies.add_argument("--area", help="Filtrar por id de area/zona")

    p_func = sub.add_parser("functions", help="Funciones de una pelicula en un cine")
    p_func.add_argument("--cinema", required=True, help="Id del cine")
    p_func.add_argument("--movie", required=True, help="Id de la pelicula")

    p_areas = sub.add_parser("areas", help="Listar areas/zonas")

    args = parser.parse_args()
    command = args.command or "movies"

    if command == "movies":
        path = f"/movies/area/{args.area}" if args.area else "/movies"
        data = http_get_json(path)
        movies = data if isinstance(data, list) else data.get("data") or []
        print(json.dumps(
            {"source": "api.cinemex.com", "total": len(movies),
             "results": [summarize_movie(m) for m in movies]},
            ensure_ascii=False, indent=2,
        ))
    elif command == "functions":
        data = http_get_json(f"/cinemas/{args.cinema}/movies/{args.movie}")
        versions = data.get("versions") if isinstance(data, dict) else []
        functions = []
        for version in versions or []:
            for session in version.get("sessions") or []:
                functions.append(summarize_function(session))
        print(json.dumps(
            {"source": "api.cinemex.com", "movie": args.movie, "cinema": args.cinema,
             "total": len(functions), "results": functions},
            ensure_ascii=False, indent=2,
        ))
    elif command == "areas":
        data = http_get_json("/states")
        print(json.dumps(
            {"source": "api.cinemex.com", "states": data if isinstance(data, list) else []},
            ensure_ascii=False, indent=2,
        ))
    else:
        parser.error(f"comando desconocido: {command}")

    if command == "movies":
        print(json.dumps(
            {"cinepolis_nota": f"Cinepolis: usa el portal oficial {CINEPOLIS_PORTAL} (su API no es publica estable)."},
            ensure_ascii=False,
        ), file=sys.stderr)


if __name__ == "__main__":
    main()
