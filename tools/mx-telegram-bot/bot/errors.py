"""Clasificación de errores de Telegram para logging y respuesta al usuario.

Los errores de red/rate-limit (NetworkError, TimedOut, RetryAfter) los reintenta
python-telegram-bot automáticamente, así que no deben registrarse como fallos
inesperados con traceback completo.
"""

from __future__ import annotations

try:
    from telegram.error import (  # type: ignore
        BadRequest,
        Forbidden,
        NetworkError,
        RetryAfter,
        TelegramError,
        TimedOut,
    )
except Exception:  # pragma: no cover - fallback si python-telegram-bot no está instalado

    class TelegramError(Exception):
        pass

    class NetworkError(TelegramError):
        pass

    class TimedOut(NetworkError):
        pass

    class RetryAfter(TelegramError):
        pass

    class Forbidden(TelegramError):
        pass

    class BadRequest(TelegramError):
        pass


TRANSIENT_ERRORS = (NetworkError, TimedOut, RetryAfter)


def is_transient(exc: BaseException | None) -> bool:
    """True para errores transitorios que se reintentan solos."""
    return isinstance(exc, TRANSIENT_ERRORS)


def describe(exc: BaseException | None) -> str:
    """Descripción corta y legible de una excepción."""
    if exc is None:
        return "desconocido"
    message = str(exc).strip() or exc.__class__.__name__
    return f"{exc.__class__.__name__}: {message}"
