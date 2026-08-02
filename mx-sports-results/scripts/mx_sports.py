#!/usr/bin/env python3
"""Consulta datos de la Liga MX y la Liga de Expansión (fútbol mexicano).

Fuente pública: API JSON de ESPN (sin API key):
  - Marcadores:  https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard?dates=YYYYMMDD
  - Posiciones:  https://site.web.api.espn.com/apis/v2/sports/soccer/{league}/standings
  - Equipos:     https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/teams

Ligas soportadas:
  - mex.1  Liga BBVA MX (Liga MX)
  - mex.2  Liga de Expansión MX

Uso:
  python3 mx_sports.py scoreboard [--league mex.1|mex.2] [--date YYYY-MM-DD] [--team <nombre>]
  python3 mx_sports.py standings  [--league mex.1|mex.2] [--team <nombre>]
  python3 mx_sports.py teams      [--league mex.1|mex.2]
"""

import argparse
import json
import re
import unicodedata
import urllib.request
from datetime import datetime, timezone

API_SITE = "https://site.api.espn.com/apis/site/v2/sports/soccer"
API_WEB = "https://site.web.api.espn.com/apis/v2/sports/soccer"
USER_AGENT = "k-skill-mx-sports-results/1.0 (+https://github.com/NomaDamas/k-skill)"

LEAGUES = {
    "mex.1": "Liga BBVA MX (Liga MX)",
    "mex.2": "Liga de Expansión MX",
}


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"La API respondió HTTP {exc.code} para {url}. Reintenta en unos minutos "
            "o consulta el sitio oficial de ESPN."
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo conectar con la API de ESPN: {exc.reason}") from exc


def _league_name(league):
    if league not in LEAGUES:
        raise SystemExit(
            f"Liga desconocida: {league}. Usa una de: {', '.join(sorted(LEAGUES))}."
        )
    return LEAGUES[league]


def _normalize(text):
    """Minúsculas y sin acentos para comparar nombres de equipos."""
    decomposed = unicodedata.normalize("NFD", text or "")
    return re.sub(r"[\u0300-\u036f]", "", decomposed).lower().strip()


def _match_team(query, *names):
    q = _normalize(query)
    if not q:
        return True
    return any(q in _normalize(n) for n in names)


def scoreboard(league, date_str, team):
    league_name = _league_name(league)
    url = (
        f"{API_SITE}/{league}/scoreboard?dates={date_str.replace('-', '')}"
    )
    data = _fetch(url)
    events = []
    for event in data.get("events") or []:
        competitors = {}
        for comp in (event.get("competitions") or [{}])[0].get("competitors") or []:
            side = comp.get("homeAway")
            if side:
                competitors[side] = comp
        away = competitors.get("away") or {}
        home = competitors.get("home") or {}
        names = [
            (away.get("team") or {}).get("displayName"),
            (home.get("team") or {}).get("displayName"),
            (away.get("team") or {}).get("abbreviation"),
            (home.get("team") or {}).get("abbreviation"),
        ]
        if not _match_team(team, *names):
            continue
        status = (event.get("status") or {}).get("type") or {}
        state = status.get("state")
        status_detail = status.get("shortDetail") or status.get("name") or ""
        season = (event.get("season") or {})
        season_name = season.get("slug", "").replace("-", " ").title() or None
        events.append(
            {
                "id": event.get("id"),
                "status": status_detail,
                "status_state": state,
                "date": event.get("date"),
                "season": season_name,
                "away_team": (away.get("team") or {}).get("displayName"),
                "home_team": (home.get("team") or {}).get("displayName"),
                "away_score": away.get("score"),
                "home_score": home.get("score"),
                "winner": (
                    "away"
                    if away.get("winner")
                    else "home"
                    if home.get("winner")
                    else None
                ),
                "venue": ((event.get("venue") or {}).get("fullName")),
            }
        )
    if not events:
        raise SystemExit(
            f"No hay partidos de {league_name} para la fecha {date_str}"
            + (f" del equipo \"{team}\"" if team else "")
            + "."
        )
    return {
        "source": url,
        "league": league_name,
        "date": date_str,
        "events": events,
    }


def _stat_map(entry):
    stats = {}
    for stat in entry.get("stats") or []:
        stats[stat.get("name")] = stat.get("displayValue")
    return stats


def standings(league, team):
    league_name = _league_name(league)
    url = f"{API_WEB}/{league}/standings"
    data = _fetch(url)
    children = data.get("children") or []
    if not children:
        raise SystemExit(f"No se encontraron posiciones de {league_name}.")
    current = children[0]
    torneo = current.get("name")
    entries = []
    for entry in (current.get("standings") or {}).get("entries") or []:
        t = entry.get("team") or {}
        if not _match_team(team, t.get("displayName"), t.get("abbreviation")):
            continue
        s = _stat_map(entry)
        entries.append(
            {
                "position": s.get("rank") or len(entries) + 1,
                "team": t.get("displayName"),
                "abbreviation": t.get("abbreviation"),
                "games": s.get("gamesPlayed"),
                "wins": s.get("wins"),
                "ties": s.get("ties"),
                "losses": s.get("losses"),
                "goals_for": s.get("pointsFor"),
                "goals_against": s.get("pointsAgainst"),
                "points": s.get("points"),
            }
        )
    if not entries:
        raise SystemExit(
            f"No se encontró el equipo \"{team}\" en las posiciones de {league_name}."
        )
    return {
        "source": url,
        "league": league_name,
        "torneo": torneo,
        "entries": entries,
    }


def teams(league):
    league_name = _league_name(league)
    url = f"{API_SITE}/{league}/teams"
    data = _fetch(url)
    result = []
    for group in (data.get("sports") or [{}])[0].get("leagues") or []:
        for item in group.get("teams") or []:
            t = item.get("team") or {}
            result.append(
                {
                    "id": t.get("id"),
                    "name": t.get("displayName"),
                    "abbreviation": t.get("abbreviation"),
                }
            )
    if not result:
        raise SystemExit(f"No se encontraron equipos de {league_name}.")
    return {"source": url, "league": league_name, "teams": result}


def _add_common(parser):
    parser.add_argument(
        "--league",
        default="mex.1",
        help="Liga: mex.1 (Liga MX) o mex.2 (Liga de Expansión)",
    )
    parser.add_argument("--team", help="Filtrar por nombre o abreviatura de equipo")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Datos de la Liga MX y la Liga de Expansión (ESPN público)"
    )
    sub = parser.add_subparsers(dest="command")

    p_score = sub.add_parser("scoreboard", help="Marcadores por fecha")
    _add_common(p_score)
    p_score.add_argument("--date", help="Fecha YYYY-MM-DD (por defecto: hoy, UTC)")

    p_stand = sub.add_parser("standings", help="Tabla de posiciones del torneo actual")
    _add_common(p_stand)

    p_teams = sub.add_parser("teams", help="Lista de equipos de la liga")
    p_teams.add_argument(
        "--league",
        default="mex.1",
        help="Liga: mex.1 (Liga MX) o mex.2 (Liga de Expansión)",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "standings"

    if command == "scoreboard":
        date_str = args.date or datetime.now(timezone.utc).date().isoformat()
        result = scoreboard(args.league, date_str, args.team)
    elif command == "standings":
        result = standings(args.league, args.team)
    elif command == "teams":
        result = teams(args.league)
    else:
        parser.error(f"comando desconocido: {command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
