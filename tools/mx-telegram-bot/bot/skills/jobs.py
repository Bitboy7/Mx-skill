"""Skill: vacantes de empleo en México (mx-job-search)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def empleo(update, context) -> str:
    query = " ".join(context.args).strip()
    if not query:
        ask("empleo", "¿Qué puesto o skill buscas? (ej. python, desarrollador, data)", kind="text")
        return ""

    data = await runner.run_skill("mx-job-search", ["--query", query, "--limit", "5", "--json"])
    results = data.get("results") or []

    if not results:
        notice = data.get("notice")
        message = f"No se encontraron vacantes para '{formatting.esc(query)}'."
        if notice:
            message += f"\n\n{formatting.esc(notice)}"
        return message

    lines = []
    for row in results:
        details = " · ".join(
            str(d) for d in (row.get("modalidad"), row.get("tipo_empleo"), row.get("ubicacion")) if d
        )
        url = row.get("url") or (data.get("official_links") or {}).get("vacantes_digitales")
        lines.append(
            f"• <b>{formatting.esc(row.get('puesto'))}</b> — {formatting.esc(row.get('empresa') or 'N/D')}\n"
            f"  {formatting.esc(details)}\n"
            f"  {formatting.esc(url)}"
        )
    return formatting.section(f"Vacantes para '{query}'", "\n\n".join(lines))


register(
    SkillEntry(
        command="empleo",
        description="Vacantes de empleo en México/LATAM (tecnología) vía Vacantes Digitales",
        usage="/empleo <puesto o skill>  (ej. /empleo python)",
        handler=empleo,
        skill_id="mx-job-search",
    )
)
