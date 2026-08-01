"""Skill: seguimiento de paquetes (delivery-tracking-mx)."""

import re

from .. import formatting, runner
from .registry import SkillEntry, register


async def envio(update, context) -> str:
    guia = (context.args[0] if context.args else "").strip()
    if not re.fullmatch(r"\d{22}", guia):
        return "Uso: <code>/envio &lt;guía de 22 dígitos&gt;</code>  (Estafeta)"

    data = await runner.run_skill("delivery-tracking-mx", ["--carrier", "estafeta", "--guia", guia])
    lines = [formatting.bullet("Mensajería", data.get("carrier") or "Estafeta")]
    if data.get("status"):
        lines.append(formatting.bullet("Estado", data.get("status")))
    for event in (data.get("recent_events") or []):
        lines.append(f"• {formatting.esc(event.get('fecha') or '')} — {formatting.esc(event.get('detalle') or '')}")
    if data.get("note"):
        lines.append(f"<i>{formatting.esc(data.get('note'))}</i>")
    return formatting.section(f"Envío {guia}", "\n".join(lines))


register(
    SkillEntry(
        command="envio",
        description="Seguimiento de paquetes en México (Estafeta)",
        usage="/envio <guía de 22 dígitos>",
        handler=envio,
        skill_id="delivery-tracking-mx",
    )
)
