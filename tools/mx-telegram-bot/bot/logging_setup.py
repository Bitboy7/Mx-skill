"""Configuración de logging del bot.

- Formato uniforme con timestamp, nivel, logger y mensaje.
- Salida a stdout (UTF-8) y, opcionalmente, a un archivo (`BOT_LOG_FILE`).
- Silencia loggers ruidosos (`httpx`, `httpcore`, `telegram`) a WARNING para que
  los errores de red transitorios no llenen la consola de trazas.
"""

from __future__ import annotations

import logging
import sys

from . import config

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"

# Loggers de librerías que emiten mucho ruido (una línea por request).
NOISY_LOGGERS = (
    "httpx",
    "httpcore",
    "telegram",
    "telegram.ext",
    "telegram.request",
    "urllib3",
    "asyncio",
)


def _resolve_level(level: str | int | None) -> int:
    if level is None:
        level = config.LOG_LEVEL
    if isinstance(level, int):
        return level
    return getattr(logging, str(level).upper(), logging.INFO)


def configure_logging(level: str | int | None = None, log_file: str | None = None) -> logging.Logger:
    """Configura el logging raíz y devuelve el logger del bot."""
    resolved = _resolve_level(level)
    formatter = logging.Formatter(LOG_FORMAT)

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        try:
            handler.close()
        except Exception:  # noqa: BLE001
            pass

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    root.addHandler(stream)
    root.setLevel(resolved)

    file_path = log_file if log_file is not None else config.LOG_FILE
    if file_path:
        try:
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except OSError:
            root.warning("No se pudo abrir BOT_LOG_FILE=%r; se registra solo en stdout", file_path)

    # Los loggers ruidosos nunca por debajo de WARNING.
    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(max(resolved, logging.WARNING))

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        pass

    return logging.getLogger("mx-bot")
