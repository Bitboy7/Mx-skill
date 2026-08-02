"""Skill: validación de RFC (sat-rfc-lookup)."""

from .. import formatting, runner
from ..interactive import ask
from .registry import SkillEntry, register


async def rfc(update, context) -> str:
    rfc_val = (context.args[0] if context.args else "").strip().upper()
    if not rfc_val:
        ask("rfc", "Escribe el RFC que quieres validar (ej. GODE561231GR8).")
        return ""

    data = await runner.run_skill("sat-rfc-lookup", ["--rfc", rfc_val])
    valid = bool(data.get("valido"))
    status = "✅ Válido (estructura)" if valid else "❌ Inválido"
    lines = [formatting.bullet("RFC", data.get("rfc")), formatting.bullet("Tipo", data.get("tipo") or "N/D")]

    if valid:
        lines.append(formatting.bullet("Iniciales", data.get("iniciales") or "N/D"))
        lines.append(formatting.bullet("Fecha (AAMMDD)", data.get("fecha_aammdd") or "N/D"))
        lines.append(formatting.bullet("Homoclave", data.get("homoclave") or "N/D"))
    lines.append(f"<i>{formatting.esc(data.get('detalle') or '')}</i>")

    return formatting.section(f"RFC {status}", "\n".join(lines))


register(
    SkillEntry(
        command="rfc",
        description="Valida la estructura de un RFC (persona física/moral, fecha)",
        usage="/rfc <RFC>  (ej. /rfc GODE561231GR8)",
        handler=rfc,
        skill_id="sat-rfc-lookup",
    )
)
