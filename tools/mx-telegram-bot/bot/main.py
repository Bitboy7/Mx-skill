"""Bot de Telegram que usa las skills MX del repositorio k-skill.

Ejecuta:  python -m bot.main   (desde tools/mx-telegram-bot)
Configura TELEGRAM_BOT_TOKEN en .env (ver .env.example).
"""

from __future__ import annotations

import re
import time

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, PicklePersistence, filters

from . import ai, config, errors, formatting, geo, interactive, logging_setup, runner
from .skills import list_skills
from .skills.registry import SkillEntry

logger = logging_setup.configure_logging()


def _summarize_args(args: list[str]) -> str:
    return " ".join(str(a)[:40] for a in args[:10])


def _allowed(user_id: int) -> bool:
    return not config.ALLOWED_USER_IDS or user_id in config.ALLOWED_USER_IDS


async def _dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE, entry: SkillEntry) -> None:
    user = update.effective_user
    user_id = getattr(user, "id", None)
    if not _allowed(user_id):
        logger.warning("acceso denegado user=%s cmd=/%s", user_id, entry.command)
        await update.effective_message.reply_text("Este bot es de uso privado.")
        return
    interactive.clear_pending(context)
    args = list(getattr(context, "args", []) or [])
    started = time.perf_counter()
    logger.info("cmd=/%s user=%s skill=%s args=[%s]", entry.command, user_id, entry.skill_id, _summarize_args(args))
    try:
        text = await entry.handler(update, context)
    except interactive.AskInput as exc:
        logger.info("cmd=/%s pide dato al usuario: %s", entry.command, exc.prompt)
        await interactive.store_and_prompt(update, context, exc)
        return
    except runner.SkillError as exc:
        logger.warning("cmd=/%s skill=%s falló: %s", entry.command, entry.skill_id, exc)
        text = f"⚠️ {exc}"
    except Exception:  # noqa: BLE001
        logger.exception("cmd=/%s skill=%s error inesperado", entry.command, entry.skill_id)
        text = "Ocurrió un error inesperado. Intenta de nuevo."
    elapsed = (time.perf_counter() - started) * 1000
    logger.info("cmd=/%s respondido en %.0f ms (%d chars)", entry.command, elapsed, len(text or ""))
    await update.effective_message.reply_text(
        text, parse_mode="HTML", disable_web_page_preview=True
    )


def _make_handler(entry: SkillEntry):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _dispatch(update, context, entry)

    return handler


async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interactive.clear_pending(context)
    await update.effective_message.reply_text(
        "🇲🇽 <b>Bot de skills MX</b>\n\n"
        "Toca un comando del menú 👇 o escribe /help para ver todo.\n\n"
        "💡 <b>Truco:</b> comparte tu 📍 ubicación y úsala en "
        "/clima, /aire, /gasolina, /ecobici y /banos.",
        parse_mode="HTML",
        reply_markup=interactive.menu_keyboard(),
    )


async def _menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interactive.clear_pending(context)
    await update.effective_message.reply_text(
        "🧭 <b>Menú de comandos</b>\nToca uno para usarlo 👇",
        parse_mode="HTML",
        reply_markup=interactive.menu_keyboard(),
    )


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(await interactive.cancel(update, context))


async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interactive.clear_pending(context)
    lines = []
    for entry in sorted(list_skills().values(), key=lambda e: e.command):
        # usage puede contener <placeholder>; escapar para parse_mode="HTML"
        lines.append(
            f"• <b>/{entry.command}</b> — {formatting.esc(entry.description)}\n"
            f"   <i>{formatting.esc(entry.usage)}</i>"
        )
    lines.append("")
    lines.append("🤖 <b>/ask</b> &lt;mensaje&gt; — enruta con IA (requiere AI_API_KEY)")
    lines.append("🧭 <b>/menu</b> — muestra los botones de comandos")
    lines.append("🚫 <b>/cancel</b> — cancela un comando en espera de datos")
    await update.effective_message.reply_text(
        "📖 <b>Comandos disponibles</b>\n\n" + "\n".join(lines),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=interactive.menu_keyboard(),
    )


async def _ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interactive.clear_pending(context)
    query = " ".join(context.args).strip()
    if not query:
        await update.effective_message.reply_text("Uso: <code>/ask &lt;mensaje&gt;</code>", parse_mode="HTML")
        return
    if not _allowed(update.effective_user.id):
        await update.effective_message.reply_text("Este bot es de uso privado.")
        return
    try:
        routed = await ai.route_query_async(query)
    except Exception as exc:  # noqa: BLE001
        await update.effective_message.reply_text(f"⚠️ {exc}")
        return

    if routed.get("skill") == "chat":
        from . import formatting

        await update.effective_message.reply_text(
            formatting.esc(routed.get("text", "…")), parse_mode="HTML"
        )
        return

    skill_id = routed.get("skill")
    args = routed.get("args") or []
    if skill_id not in runner.SKILL_SCRIPTS:
        await update.effective_message.reply_text(
            f"El modelo eligió una skill desconocida: {skill_id}"
        )
        return
    try:
        data = await runner.run_skill(skill_id, args)
        from . import formatting

        await update.effective_message.reply_text(formatting.mono(data), parse_mode="HTML")
    except runner.SkillError as exc:
        await update.effective_message.reply_text(f"⚠️ {exc}")


async def _on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = getattr(update.effective_user, "id", None)
    if not _allowed(user_id):
        logger.warning("acceso denegado user=%s (texto)", user_id)
        await update.effective_message.reply_text("Este bot es de uso privado.")
        return
    incoming = update.effective_message.text.strip()
    logger.info("texto user=%s: %r", user_id, incoming[:80])

    # Botones del menú con emoji: "🌤 /clima" -> ejecuta /clima.
    match = re.match(r"^\W*\s*/([A-Za-z_]+)(?:\s+(.*))?$", incoming)
    if match:
        command = match.group(1)
        rest = (match.group(2) or "").strip()
        handlers = {"start": _start, "help": _help, "menu": _menu, "cancel": _cancel, "ask": _ask}
        entry = list_skills().get(command)
        if command in handlers or entry is not None:
            context.args = rest.split() if rest else []
            logger.info("botón de menú user=%s cmd=/%s", user_id, command)
            if entry is not None:
                await _dispatch(update, context, entry)
            else:
                await handlers[command](update, context)
            return

    try:
        text = await interactive.resume(
            update, context, text=incoming
        )
    except interactive.AskInput as exc:
        logger.info("texto user=%s sigue pidiendo dato: %s", user_id, exc.prompt)
        await interactive.store_and_prompt(update, context, exc)
        return
    except runner.SkillError as exc:
        logger.warning("texto user=%s falló: %s", user_id, exc)
        text = f"⚠️ {exc}"
    except Exception:  # noqa: BLE001
        logger.exception("error completando comando pendiente user=%s", user_id)
        text = "Ocurrió un error inesperado. Intenta de nuevo."
    if text is None:
        logger.info("texto sin comando pendiente user=%s", user_id)
        await update.effective_message.reply_text(
            "No entiendo. Toca un botón del menú (usa /menu) o escribe /help "
            "para ver los comandos."
        )
        return
    await update.effective_message.reply_text(
        text, parse_mode="HTML", disable_web_page_preview=True
    )


async def _on_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = getattr(update.effective_user, "id", None)
    if not _allowed(user_id):
        logger.warning("acceso denegado user=%s (ubicación)", user_id)
        await update.effective_message.reply_text("Este bot es de uso privado.")
        return
    loc = update.effective_message.location
    result = await interactive.resume(
        update, context, location=(loc.latitude, loc.longitude)
    )
    if result is not None:
        logger.info("ubicación usada para completar comando user=%s", user_id)
        await update.effective_message.reply_text(
            result, parse_mode="HTML", disable_web_page_preview=True
        )
        return
    snapshot = geo.save(context, loc.latitude, loc.longitude)
    logger.info("ubicación guardada user=%s (%s)", user_id, geo.describe(snapshot))
    await update.effective_message.reply_text(
        "📍 Ubicación guardada (aproximada):\n"
        f"<code>{geo.describe(snapshot)}</code>\n\n"
        "Ahora puedes usar <b>/gasolina</b>, <b>/ecobici</b>, <b>/clima</b>, "
        "<b>/aire</b>, <b>/banos</b> o <b>/ruta a &lt;destino&gt;</b> sin escribir el lugar.",
        parse_mode="HTML",
    )


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    exc = context.error
    if errors.is_transient(exc):
        # Fallos de red/rate-limit: python-telegram-bot los reintenta solo.
        logger.warning("Telegram transitorio (se reintenta solo): %s", errors.describe(exc))
        return
    logger.error("error no controlado: %s", errors.describe(exc), exc_info=exc)
    message = getattr(update, "effective_message", None)
    if message is not None:
        try:
            await message.reply_text("⚠️ Ocurrió un error interno. Vuelve a intentarlo.")
        except Exception:  # noqa: BLE001
            logger.debug("no se pudo avisar al usuario tras el error", exc_info=True)


def build_app() -> Application:
    if not config.BOT_TOKEN:
        raise SystemExit(
            "Falta TELEGRAM_BOT_TOKEN. Copia .env.example a .env y llénalo "
            "(consigue el token con @BotFather)."
        )

    builder = Application.builder().token(config.BOT_TOKEN)
    if config.PERSISTENCE_FILE:
        builder = builder.persistence(PicklePersistence(filepath=config.PERSISTENCE_FILE))
    app = builder.build()

    app.add_error_handler(_on_error)

    for entry in list_skills().values():
        app.add_handler(CommandHandler(entry.command, _make_handler(entry)))

    app.add_handler(MessageHandler(filters.LOCATION, _on_location))
    app.add_handler(CommandHandler("start", _start))
    app.add_handler(CommandHandler("help", _help))
    app.add_handler(CommandHandler("menu", _menu))
    app.add_handler(CommandHandler("cancel", _cancel))
    app.add_handler(CommandHandler("ask", _ask))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _on_text))
    return app


def _log_startup_summary() -> None:
    skills = list_skills()
    logger.info(
        "Comandos registrados (%d): %s",
        len(skills),
        ", ".join(sorted("/" + command for command in skills)),
    )
    logger.info(
        "Config: lugar_por_defecto=%r whitelist=%d persistencia=%s ia=%s log_level=%s log_file=%s",
        config.DEFAULT_PLACE,
        len(config.ALLOWED_USER_IDS),
        config.PERSISTENCE_FILE or "memoria",
        "activa" if config.AI_API_KEY else "desactivada",
        config.LOG_LEVEL,
        config.LOG_FILE or "solo stdout",
    )


def main() -> None:
    logger.info("Iniciando bot de skills MX ...")
    _log_startup_summary()
    app = build_app()
    logger.info("Bot iniciado. Ctrl+C para detener. Esperando actualizaciones ...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
