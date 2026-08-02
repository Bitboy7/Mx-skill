"""Skill: fútbol mexicano (Liga MX / Liga de Expansión) via mx-sports-results."""

from .. import formatting, runner
from .registry import SkillEntry, register

_STATE = {"pre": "Programado", "in": "En juego", "post": "Final"}


async def _standings(league: str, team: str = "") -> str:
    args = ["standings", "--league", league]
    if team:
        args += ["--team", team]
    data = await runner.run_skill("mx-sports-results", args)
    lines = [formatting.section(f"{data.get('league')} — {data.get('torneo')}", "")]
    for entry in data.get("entries") or []:
        lines.append(
            f"{entry.get('position')}. <b>{formatting.esc(entry.get('team'))}</b> "
            f"— {entry.get('points')} pts "
            f"({entry.get('games')} PJ, {entry.get('wins')}G {entry.get('ties')}E {entry.get('losses')}P · "
            f"{entry.get('goals_for')}:{entry.get('goals_against')})"
        )
    return "\n".join(lines)


async def _scoreboard(league: str, team: str = "") -> str:
    args = ["scoreboard", "--league", league]
    if team:
        args += ["--team", team]
    data = await runner.run_skill("mx-sports-results", args)
    lines = [formatting.section(f"{data.get('league')} — {data.get('date')}", "")]
    for event in data.get("events") or []:
        state = _STATE.get(event.get("status_state"), event.get("status"))
        home = event.get("home_team")
        away = event.get("away_team")
        if event.get("home_score") is None:
            score = "vs"
        else:
            score = f"{event.get('home_score')} – {event.get('away_score')}"
        lines.append(
            f"• <b>{state}</b>: {formatting.esc(home)} {score} {formatting.esc(away)}"
        )
    return "\n".join(lines)


async def futbol(update, context) -> str:
    args = [a.lower() for a in context.args]
    if not args:
        return await _standings("mex.1")
    first = args[0]
    if first in ("jornada", "resultados", "partidos", "hoy"):
        return await _scoreboard("mex.1")
    if first in ("expansion", "liga-expansion", "expansión"):
        return await _standings("mex.2")
    return await _standings("mex.1", team=" ".join(context.args))


register(
    SkillEntry(
        command="futbol",
        description="Liga MX / fútbol mexicano: tabla, posición de un equipo o jornada",
        usage="/futbol  |  /futbol america  |  /futbol jornada  |  /futbol expansion",
        handler=futbol,
        skill_id="mx-sports-results",
    )
)
