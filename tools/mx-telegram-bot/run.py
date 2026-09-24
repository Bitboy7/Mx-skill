#!/usr/bin/env python3
"""Arranque rápido del bot de Telegram de skills MX.

Hace todo el setup por ti y luego inicia el bot:

  1. Crea `.venv` si no existe.
  2. Instala/actualiza `requirements.txt` cuando cambia.
  3. Crea `.env` a partir de `.env.example` si falta.
  4. Verifica que `TELEGRAM_BOT_TOKEN` esté configurado.
  5. Ejecuta el bot (`python -m bot.main`).

Uso:
  python run.py                # setup + iniciar el bot
  python run.py --smoke        # setup + smoke test (sin Telegram)
  python run.py --check        # solo verificar el entorno
  python run.py --no-install   # no tocar dependencias
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

BOT_DIR = Path(__file__).resolve().parent
VENV_DIR = BOT_DIR / ".venv"
REQUIREMENTS = BOT_DIR / "requirements.txt"
ENV_FILE = BOT_DIR / ".env"
ENV_EXAMPLE = BOT_DIR / ".env.example"
REQ_MARKER = VENV_DIR / ".requirements.sha256"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def log(message: str) -> None:
    print(f"[run] {message}", flush=True)


def ensure_venv() -> Path:
    python = venv_python()
    if python.exists():
        return python
    log(f"Creando entorno virtual en {VENV_DIR} ...")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    if not python.exists():
        raise SystemExit("No se pudo crear el entorno virtual.")
    return python


def requirements_hash() -> str:
    return hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()


def ensure_requirements(python: Path, install: bool = True) -> None:
    current = requirements_hash()
    if REQ_MARKER.exists() and REQ_MARKER.read_text(encoding="utf-8").strip() == current:
        return
    if not install:
        log("Dependencias posiblemente desactualizadas (se omitió --install).")
        return
    log("Instalando dependencias ...")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", "-r", str(REQUIREMENTS)],
        check=True,
    )
    REQ_MARKER.write_text(current, encoding="utf-8")
    log("Dependencias listas.")


def ensure_env() -> None:
    if ENV_FILE.exists():
        return
    if not ENV_EXAMPLE.exists():
        return
    shutil.copyfile(ENV_EXAMPLE, ENV_FILE)
    log(f"Creado {ENV_FILE.name} a partir de {ENV_EXAMPLE.name}.")


def read_env_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token
    if not ENV_FILE.exists():
        return ""
    for line in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "TELEGRAM_BOT_TOKEN":
            return value.strip().strip('"').strip("'")
    return ""


def check_token() -> bool:
    token = read_env_token()
    if token:
        log("TELEGRAM_BOT_TOKEN configurado.")
        return True
    log("Falta TELEGRAM_BOT_TOKEN.")
    log(f"Edita {ENV_FILE} y pega el token que te dio @BotFather en Telegram.")
    return False


def run_bot(python: Path) -> int:
    log("Iniciando el bot (Ctrl+C para detener) ...")
    return subprocess.call([str(python), "-m", "bot.main"], cwd=str(BOT_DIR))


def run_smoke(python: Path) -> int:
    log("Ejecutando smoke test (sin Telegram) ...")
    return subprocess.call([str(python), "smoke_test.py"], cwd=str(BOT_DIR))


def main() -> int:
    parser = argparse.ArgumentParser(description="Arranque rápido del bot MX de Telegram")
    parser.add_argument("--smoke", action="store_true", help="Ejecutar el smoke test en vez del bot")
    parser.add_argument("--check", action="store_true", help="Solo verificar el entorno")
    parser.add_argument("--no-install", action="store_true", help="No instalar/actualizar dependencias")
    args = parser.parse_args()

    python = ensure_venv()
    ensure_requirements(python, install=not args.no_install)
    ensure_env()

    token_ok = check_token()
    if args.check:
        return 0 if token_ok else 1

    if not token_ok:
        return 1

    if args.smoke:
        return run_smoke(python)
    return run_bot(python)


if __name__ == "__main__":
    raise SystemExit(main())
