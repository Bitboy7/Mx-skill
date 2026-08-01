"""Skill: candidatas y candidatos del INE (comision-ine)."""

from .. import formatting, runner
from .registry import SkillEntry, register

TIPOS = {"presidente", "senadores", "senadores_mr", "diputados", "diputados_mr"}


async def candidatos(update, context) -> str:
    args = list(context.args)

    tipo = None
    if args and args[0].startswith("--"):
        raw = args.pop(0)
        if "=" in raw:
            tipo = raw.split("=", 1)[1]
        elif args:
            tipo = args.pop(0)
    elif args and args[0].lower() in TIPOS:
        tipo = args.pop(0).lower()

    name = " ".join(args).strip()

    skill_args = []
    if name:
        skill_args += ["--name", name]
    if tipo:
        skill_args += ["--tipo", tipo]
    if not name and not tipo:
        skill_args += ["--all", "--tipo", "presidente"]

    data = await runner.run_skill("comision-ine", skill_args)
    results = data.get("results") or []
    if not results:
        return f"No se encontraron candidatos{f' para {name}' if name else ''}."

    lines = []
    for c in results[:8]:
        props = c.get("propuestas") or []
        prop_summary = ""
        if props:
            prop_summary = f"\n  💬 {formatting.esc(props[0][:140])}…"
        lines.append(
            f"• <b>{formatting.esc(c.get('nombre'))}</b> ({formatting.esc(c.get('partido') or 'N/D')}) · {c.get('edad')} años{prop_summary}"
        )
    return formatting.section(f"Candidatos del INE ({data.get('total')} resultado(s))", "\n".join(lines))


register(
    SkillEntry(
        command="candidatos",
        description="Candidatas y candidatos del INE por nombre o tipo",
        usage="/candidatos <nombre>  o  /candidatos presidente",
        handler=candidatos,
        skill_id="comision-ine",
    )
)
