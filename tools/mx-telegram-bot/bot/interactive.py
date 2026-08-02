"""Interactividad del bot: menú de comandos y completado guiado de parámetros.

Flujo "entrada pendiente": cuando un comando necesita un parámetro y no lo
recibe, el handler lanza `AskInput`; el bot guarda el comando pendiente en
`context.user_data` y pregunta. El siguiente mensaje de texto (o ubicación 📍)
del usuario retoma el comando con el dato faltante vía `resume()`.
"""

from __future__ import annotations

from telegram import ReplyKeyboardMarkup

from . import geo

PENDING_KEY = "pending_command"


class AskInput(Exception):
    """Lanzado por un handler cuando faltan parámetros para completar el comando.

    - `command`: comando a retomar (p. ej. "cp").
    - `prompt`: texto de la pregunta que se muestra al usuario.
    - `kind`: cómo interpretar la respuesta: "text" (libre), "place"
      (lugar, acepta 📍) o "route" (destino, acepta 📍 como origen).
    """

    def __init__(self, command: str, prompt: str, kind: str = "text") -> None:
        super().__init__(prompt)
        self.command = command
        self.prompt = prompt
        self.kind = kind


def ask(command: str, prompt: str, kind: str = "text") -> None:
    """Lanza `AskInput`. Los handlers lo usan en lugar de devolver 'Uso: ...'."""
    raise AskInput(command, prompt, kind)


def clear_pending(context) -> bool:
    """Descarta cualquier comando pendiente. Devuelve True si había uno."""
    if hasattr(context, "user_data") and context.user_data.pop(PENDING_KEY, None) is not None:
        return True
    return False


def menu_keyboard() -> ReplyKeyboardMarkup:
    """Botones con los comandos principales (sin necesidad de escribirlos)."""
    rows = [
        ["/clima", "/futbol"],
        ["/ecobici", "/gasolina"],
        ["/melate", "/noticias"],
        ["/cine", "/canasta"],
        ["/cp", "/rfc"],
        ["/precio", "/inmuebles"],
        ["/envio", "/ruta"],
        ["/candidatos", "/help"],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


async def store_and_prompt(update, context, exc: AskInput) -> None:
    """Responde la pregunta del handler y guarda el comando pendiente."""
    if hasattr(context, "user_data"):
        context.user_data[PENDING_KEY] = {"command": exc.command, "kind": exc.kind}
    text = exc.prompt
    if exc.kind in ("place", "route"):
        text += "\n\nPuedes escribir el lugar o compartir tu ubicación 📍."
    await update.effective_message.reply_text(text)


async def cancel(update, context) -> str:
    """Cancela el comando pendiente, si lo hay."""
    if clear_pending(context):
        return "Operación cancelada. Usa /menu para ver los comandos."
    return "No hay ninguna operación pendiente de completar."


async def resume(update, context, text: str | None = None, location=None) -> str | None:
    """Retoma el comando pendiente con la respuesta del usuario.

    Devuelve el texto de respuesta, o None si no hay comando pendiente.
    Si la respuesta no basta, el comando se deja pendiente y se devuelve un
    mensaje pidiendo el dato que falta.
    """
    if not hasattr(context, "user_data") or PENDING_KEY not in context.user_data:
        return None
    pending = context.user_data.pop(PENDING_KEY)

    from .skills import list_skills

    entry = list_skills().get(pending["command"])
    if entry is None:
        return None
    kind = pending.get("kind", "text")

    args: list[str] = []
    if location is not None:
        geo.save(context, location[0], location[1])
        if kind == "route" and not text:
            context.user_data[PENDING_KEY] = pending
            return "📍 Ubicación guardada. ¿A dónde quieres ir?"
        if kind == "route":
            args = ["a", text]
        elif kind == "place":
            args = []
        else:
            args = [text] if text else []
    else:
        args = [text] if text else []

    if not args and not (location is not None and kind == "place"):
        context.user_data[PENDING_KEY] = pending
        return "Escribe el dato que falta o comparte tu ubicación 📍 para continuar."

    context.args = args
    return await entry.handler(update, context)
