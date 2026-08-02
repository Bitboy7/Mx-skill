"""Smoke test del bot sin Telegram: ejecuta los handlers con un fake context.

Uso:  python smoke_test.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:  # pragma: no cover
    pass

import bot.interactive as interactive  # noqa: E402
import bot.runner as runner  # noqa: E402
import bot.skills as skills  # noqa: E402


class FakeContext:
    def __init__(self, args, user_data=None):
        self.args = args
        self.user_data = user_data if user_data is not None else {}


async def run_handler(name, args, user_data=None):
    entry = skills.list_skills().get(name)
    if not entry:
        print(f"[{name}] no registrada")
        return
    text = await entry.handler(None, FakeContext(args, user_data))
    preview = text.replace("\n", " ")[:200]
    print(f"\n=== /{name} {' '.join(args)!r} ===")
    print(preview + ("…" if len(preview) == 200 else ""))


async def main():
    saved_location = None
    cases = [
        ("clima", ["Guadalajara"]),
        ("noticias", ["economia mexico"]),
        ("melate", ["6", "14", "21", "32", "40", "49"]),
        ("cp", ["06600"]),
        ("rfc", ["GODE561231GR8"]),
        ("ecobici", ["Roma Norte"]),
        ("cine", []),
        ("candidatos", ["Claudia"]),
        ("envio", ["0000000000000000000000"]),
        ("futbol", []),
        ("futbol", ["america"]),
    ]
    for name, args in cases:
        try:
            await run_handler(name, args)
        except runner.SkillError as exc:
            print(f"\n=== /{name} => SkillError: {exc}")
        except SystemExit as exc:
            print(f"\n=== /{name} => SystemExit: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"\n=== /{name} => ERROR {type(exc).__name__}: {exc}")

    # --- Ubicación compartida: guardar y usar en skills de cercanía ---
    import bot.geo as geo

    ctx = FakeContext([], {})
    snapshot = geo.save(ctx, 19.4300, -99.1600)
    print(f"\n[ubicación guardada] {geo.describe(snapshot)}")
    for name, args in [
        ("clima", []),
        ("ecobici", []),
        ("gasolina", []),
        ("ruta", ["a", "Zocalo"]),
    ]:
        try:
            await run_handler(name, args, user_data=ctx.user_data)
        except runner.SkillError as exc:
            print(f"\n=== /{name} (con ubicación) => SkillError: {exc}")

    # --- Flujo interactivo: comandos sin parámetros piden el dato ---
    print("\n=== Interactivo: comandos sin parámetros piden el dato ===")
    for name in ["cp", "rfc", "precio", "inmuebles", "clima", "ruta"]:
        entry = skills.list_skills().get(name)
        try:
            await entry.handler(None, FakeContext([], {}))
            print(f"/{name}: (no pidió dato)")
        except interactive.AskInput as exc:
            print(f"/{name}: ASK -> {exc.prompt[:90]}")

    # --- Interactivo: responder completa el comando pendiente ---
    print("\n=== Interactivo: responder completa el comando pendiente ===")
    pending = interactive.PENDING_KEY
    ctx_cp = FakeContext([], {})
    ctx_cp.user_data[pending] = {"command": "cp", "kind": "text"}
    result = await interactive.resume(None, ctx_cp, text="06600")
    print(f"resume /cp '06600' -> {result[:90] if result else None}")

    ctx_ruta = FakeContext([], {})
    ctx_ruta.user_data[pending] = {"command": "ruta", "kind": "route"}
    result = await interactive.resume(None, ctx_ruta, location=(19.43, -99.16), text="Zocalo")
    print(f"resume /ruta + 📍 'Zocalo' -> {result[:90] if result else None}")

    result = await interactive.resume(None, FakeContext([], {}), text="hola")
    print(f"resume sin pendiente -> {result!r}")


if __name__ == "__main__":
    asyncio.run(main())
