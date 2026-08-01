"""Utilidades de formato para respuestas de Telegram (parse_mode="HTML")."""

from __future__ import annotations

import html
import json

from . import config


def esc(text: object) -> str:
    """Escapa texto para Telegram HTML."""
    return html.escape(str(text), quote=False)


def _clip(text: str) -> str:
    if len(text) <= config.MAX_REPLY_LEN:
        return text
    return text[: config.MAX_REPLY_LEN - 1] + "…"


def mono(data: object) -> str:
    """JSON bonito en bloque <pre>."""
    return _clip(f"<pre>{esc(json.dumps(data, ensure_ascii=False, indent=2))}</pre>")


def section(title: str, body: str) -> str:
    return f"<b>{esc(title)}</b>\n{body}"


def bullet(key: str, value: object) -> str:
    return f"• {esc(key)}: <b>{esc(value)}</b>"


def list_bullets(items: list[str]) -> str:
    return "\n".join(f"• {item}" for item in items)


def numbers_table(rows: list[list[str]]) -> str:
    """Tabla sencilla de columnas alineadas con separador ' · '."""
    return "\n".join(" · ".join(esc(cell) for cell in row) for row in rows)
