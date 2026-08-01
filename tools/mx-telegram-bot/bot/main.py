"""Bot de Telegram que usa las skills MX del repositorio k-skill.

Ejecuta:  python -m bot.main   (desde tools/mx-telegram-bot)
Configura TELEGRAM_BOT_TOKEN en .env (ver .env.example).
"""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, PicklePersistence, filters

from . import ai, config, formatting, geo, runner
from .skills import list_skills
from .skills.registry import SkillEntry

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("mx-bot")


def _allowed(user_id: int) -> bool:
    return not config.ALLOWED_USER_IDS or user_id in config.ALLOWED_USER_IDS


async def _dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE, entry: SkillEntry) -> None:
    user = update.effective_user
    if not _allowed(user.id):
        await update.effective_message.reply_text("Este bot es de uso privado.")
        return
    try:
        text = await entry.handler(update, context)
    except runner.SkillError as exc:
        text = f"⚠️ {exc}"
    except Exception:  # noqa: BLE001
        logger.exception("error ejecutando /%s", entry.command)
        text = "Ocurrió un error inesperado. Intenta de nuevo."
    await update.effective_message.reply_text(
        text, parse_mode="HTML", disable_web_page_preview=True
    )


def _make_handler(entry: SkillEntry):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _dispatch(update, context, entry)

    return handler


async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "¡Hola! Soy el bot de skills MX 🇲🇽\nUsa /help para ver los comandos."
    )


async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = []
    for entry in sorted(list_skills().values(), key=lambda e: e.command):
        # usage puede contener <placeholder>; escapar para parse_mode="HTML"
        lines.append(
            f"/{entry.command} — {formatting.esc(entry.description)}\n"
            f"   <i>{formatting.esc(entry.usage)}</i>"
        )
    lines.append("/ask &lt;mensaje&gt; — enruta con IA a la skill correcta (requiere AI_API_KEY)")
    await update.effective_message.reply_text(
        "\n".join(lines), parse_mode="HTML", disable_web_page_preview=True
    )


async def _ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        await update.effective_message.reply_text(routed.get("text", "…"))
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


async def _on_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update.effective_user.id):
        await update.effective_message.reply_text("Este bot es de uso privado.")
        return
    loc = update.effective_message.location
    snapshot = geo.save(context, loc.latitude, loc.longitude)
    await update.effective_message.reply_text(
        "📍 Ubicación guardada (aproximada):\n"
        f"<code>{geo.describe(snapshot)}</code>\n\n"
        "Ahora puedes usar <b>/gasolina</b>, <b>/ecobici</b>, <b>/clima</b> o "
        "<b>/ruta a &lt;destino&gt;</b> sin escribir el lugar.",
        parse_mode="HTML",
    )


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("error no controlado: %s", context.error, exc_info=context.error)
    if update is not None and hasattr(update, "effective_message"):
        try:
            await update.effective_message.reply_text(
                "⚠️ Ocurrió un error interno. Vuelve a intentarlo."
            )
        except Exception:  # noqa: BLE001
            pass


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
    app.add_handler(CommandHandler("ask", _ask))
    return app


def main() -> None:
    app = build_app()
    logger.info("Bot iniciado. Ctrl+C para detener.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
