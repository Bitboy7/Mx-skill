"""Stub mínimo de `telegram` / `telegram.ext` / `telegram.error` para tests.

Permite importar los módulos del bot sin instalar python-telegram-bot. Solo
provee los atributos que se usan a nivel de import y en los handlers de error.
"""

from __future__ import annotations

import sys
import types


def install() -> None:
    if "telegram" in sys.modules:
        return

    telegram = types.ModuleType("telegram")

    class Update:  # noqa: D401
        pass

    class ReplyKeyboardMarkup:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class BotCommand:
        def __init__(self, command, description=None):
            self.command = command
            self.description = description

    class ForceReply:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    telegram.Update = Update
    telegram.ReplyKeyboardMarkup = ReplyKeyboardMarkup
    telegram.BotCommand = BotCommand
    telegram.ForceReply = ForceReply

    error = types.ModuleType("telegram.error")

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

    error.TelegramError = TelegramError
    error.NetworkError = NetworkError
    error.TimedOut = TimedOut
    error.RetryAfter = RetryAfter
    error.Forbidden = Forbidden
    error.BadRequest = BadRequest
    telegram.error = error

    ext = types.ModuleType("telegram.ext")

    class _Dummy:
        def __init__(self, *args, **kwargs):
            pass

    class ContextTypes:
        DEFAULT_TYPE = object

    ext.Application = _Dummy
    ext.CommandHandler = _Dummy
    ext.MessageHandler = _Dummy
    ext.PicklePersistence = _Dummy
    ext.ContextTypes = ContextTypes
    ext.filters = _Dummy()

    telegram.ext = ext

    sys.modules["telegram"] = telegram
    sys.modules["telegram.error"] = error
    sys.modules["telegram.ext"] = ext
