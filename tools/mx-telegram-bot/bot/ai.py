"""Capa de IA opcional: enruta un mensaje libre a la skill correcta.

Usa una API compatible con OpenAI (/chat/completions) vía urllib (sin
dependencias extra). Funciona con OpenAI, Ollama, LM Studio, etc. Solo se
activa si hay AI_API_KEY configurada.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import urllib.error
import urllib.request

from . import config
from .skills import list_skills

logger = logging.getLogger("mx-bot.ai")


def _build_catalog() -> str:
    lines = []
    for entry in list_skills().values():
        lines.append(f"- {entry.skill_id}: {entry.description}  (uso: {entry.usage})")
    return "\n".join(lines)


SYSTEM_PROMPT = (
    "Eres un enrutador de un bot de Telegram con skills de información sobre México. "
    "Habla con lenguaje ameno y cordial, usa palabras o modismos mexicanos para una "
    "mayor credibilidad y confianza. "
    "Dado el mensaje del usuario y el catálogo de skills, responde EXCLUSIVAMENTE con JSON:\n"
    '{{"skill": "<skill_id>", "args": ["--flag", "valor", ...]}}\n'
    'Si ninguna skill aplica, responde: {{"skill": "chat", "text": "<respuesta breve en español>"}}\n'
    'El campo "args" son los flags de línea de comandos del helper (p. ej. --place, --q, --limit); '
    "usa solo flags que la skill acepte según su uso, y no inventes valores. "
    "No añadas texto fuera del JSON.\n\n"
    "Catálogo de skills (skill_id):\n{catalog}"
)


def _api_error_message(exc: urllib.error.HTTPError) -> str:
    """Extrae el mensaje de error que devuelve la API (si es JSON)."""
    try:
        body = exc.read().decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        body = ""
    try:
        parsed = json.loads(body)
        error = parsed.get("error")
        if isinstance(error, dict) and error.get("message"):
            return str(error["message"])
    except (ValueError, AttributeError):
        pass
    return body.strip()[:300] or f"HTTP {exc.code}"


def _call_chat(messages: list[dict]) -> str:
    url = f"{config.AI_BASE_URL.rstrip('/')}/chat/completions"
    body: dict = {"model": config.AI_MODEL, "messages": messages}
    # Solo se envía temperature si el usuario la configuró: algunos modelos
    # (p. ej. gpt-6-luna) rechazan valores distintos al default con HTTP 400.
    if config.AI_TEMPERATURE is not None:
        body["temperature"] = config.AI_TEMPERATURE

    payload = json.dumps(body).encode("utf-8")
    logger.info(
        "IA request model=%s url=%s messages=%d chars=%d",
        config.AI_MODEL, url, len(messages), len(payload),
    )
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.AI_API_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = _api_error_message(exc)
        logger.error("IA HTTP %s en %s: %s", exc.code, url, detail)
        raise RuntimeError(f"La API de IA respondió HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        logger.error("IA error de red en %s: %s", url, exc)
        raise RuntimeError(
            f"No se pudo conectar a la API de IA ({config.AI_BASE_URL}): {exc.reason}"
        ) from exc
    except TimeoutError as exc:
        logger.error("IA timeout en %s", url)
        raise RuntimeError("La API de IA tardó demasiado en responder.") from exc

    try:
        data = json.loads(raw.decode("utf-8", "ignore"))
        content = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        logger.error("IA respuesta inesperada: %.300s", raw[:300])
        raise RuntimeError("La API de IA devolvió una respuesta inesperada.") from exc

    logger.info("IA respuesta %d chars", len(content or ""))
    if not content:
        logger.error("IA sin contenido: %.300s", raw[:300])
        raise RuntimeError("La API de IA no devolvió contenido.")
    return content


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
    catalog = _build_catalog()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(catalog=catalog)},
        {"role": "user", "content": query},
    ]
    logger.debug("IA catálogo %d chars; consulta %d chars", len(catalog), len(query))
    content = _call_chat(messages)
    try:
        routed = _extract_json(content)
    except ValueError:
        logger.error("IA no devolvió JSON válido: %.300s", content)
        raise
    logger.info("IA enrutado skill=%s args=%s", routed.get("skill"), routed.get("args"))
    return routed


async def route_query_async(query: str) -> dict:
    return await asyncio.to_thread(route_query, query)
