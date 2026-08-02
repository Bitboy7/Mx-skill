"""Capa de IA opcional: enruta un mensaje libre a la skill correcta.

Usa una API compatible con OpenAI (/chat/completions) vía urllib (sin
dependencias extra). Funciona con OpenAI, Ollama, LM Studio, etc. Solo se
activa si hay AI_API_KEY configurada.
"""

from __future__ import annotations

import asyncio
import json
import re
import urllib.request

from . import config
from .skills import list_skills


def _build_catalog() -> str:
    lines = []
    for entry in list_skills().values():
        lines.append(f"- {entry.skill_id}: {entry.description}  (uso: {entry.usage})")
    return "\n".join(lines)


SYSTEM_PROMPT = (
    "Eres un enrutador de un bot de Telegram con skills de información sobre México. "
    "Dado el mensaje del usuario y el catálogo de skills, responde EXCLUSIVAMENTE con JSON:\n"
    '{{"skill": "<skill_id>", "args": ["--flag", "valor", ...]}}\n'
    'Si ninguna skill aplica, responde: {{"skill": "chat", "text": "<respuesta breve en español>"}}\n'
    'El campo "args" son los flags de línea de comandos del helper (p. ej. --place, --q, --limit); '
    "usa solo flags que la skill acepte según su uso, y no inventes valores. "
    "No añadas texto fuera del JSON.\n\n"
    "Catálogo de skills (skill_id):\n{catalog}"
)


def _call_chat(messages: list[dict]) -> str:
    url = f"{config.AI_BASE_URL.rstrip('/')}/chat/completions"
    payload = json.dumps(
        {
            "model": config.AI_MODEL,
            "messages": messages,
            "temperature": 0,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.AI_API_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("El modelo no devolvió JSON válido.")
    return json.loads(text[start : end + 1])


def route_query(query: str) -> dict:
    """Devuelve {"skill": id, "args": [...]} o {"skill": "chat", "text": ...}."""
    if not config.AI_API_KEY:
        raise RuntimeError(
            "La capa de IA no está configurada. Añade AI_API_KEY en .env "
            "(OpenAI o una API compatible como Ollama)."
        )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(catalog=_build_catalog())},
        {"role": "user", "content": query},
    ]
    content = _call_chat(messages)
    return _extract_json(content)


async def route_query_async(query: str) -> dict:
    return await asyncio.to_thread(route_query, query)
