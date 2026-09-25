"""Pruebas del flujo guiado y el límite de tasa de /ask (sin red ni Telegram)."""

import pathlib
import sys
import unittest
from unittest import mock

import _telegram_stub

_telegram_stub.install()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import telegram  # noqa: E402

import bot.config as config  # noqa: E402
import bot.interactive as interactive  # noqa: E402
import bot.main as main  # noqa: E402
import bot.ratelimit as ratelimit  # noqa: E402
import bot.skills as skills  # noqa: E402


class FakeMessage:
    def __init__(self, text=""):
        self.text = text
        self.replies = []
        self.reply_markups = []

    async def reply_text(self, *args, **kwargs):
        self.replies.append(args[0] if args else "")
        self.reply_markups.append(kwargs.get("reply_markup"))


class FakeUser:
    id = 4242


class FakeUpdate:
    def __init__(self, text=""):
        self.effective_user = FakeUser()
        self.effective_message = FakeMessage(text)


class FakeContext:
    def __init__(self, args=None):
        self.args = args or []
        self.user_data = {}


async def fake_route(query):
    return {"skill": "chat", "text": f"respuesta a: {query}"}


class AskFlowTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._key = mock.patch.object(config, "AI_API_KEY", "test-key")
        self._key.start()
        self.addCleanup(self._key.stop)
        self._old_limiter = main.ask_limiter
        main.ask_limiter = ratelimit.RateLimiter(5, 60)
        self.addCleanup(setattr, main, "ask_limiter", self._old_limiter)

    async def test_ask_without_args_prompts_and_sets_pending(self):
        update = FakeUpdate()
        context = FakeContext()
        with mock.patch.object(main.ai, "route_query_async", side_effect=AssertionError("no debe llamar IA")):
            await main._ask(update, context)

        self.assertIn(interactive.PENDING_KEY, context.user_data)
        self.assertEqual(context.user_data[interactive.PENDING_KEY]["command"], "ask")
        self.assertIn("¿Qué quieres preguntar", update.effective_message.replies[0])

    async def test_pending_ask_uses_next_text_message(self):
        context = FakeContext()
        interactive.set_pending(context, "ask")
        update = FakeUpdate("Como automatizo la contabilidad?")
        with mock.patch.object(main.ai, "route_query_async", new=fake_route):
            await main._on_text(update, context)

        self.assertIn("respuesta a: Como automatizo la contabilidad?", update.effective_message.replies[-1])
        self.assertNotIn(interactive.PENDING_KEY, context.user_data)

    async def test_ask_with_args_calls_ai(self):
        update = FakeUpdate()
        context = FakeContext(["hola", "mundo"])
        with mock.patch.object(main.ai, "route_query_async", new=fake_route):
            await main._ask(update, context)

        self.assertIn("respuesta a: hola mundo", update.effective_message.replies[-1])

    async def test_ask_rate_limit_blocks(self):
        main.ask_limiter = ratelimit.RateLimiter(2, 60)
        with mock.patch.object(main.ai, "route_query_async", new=fake_route):
            for _ in range(2):
                await main._ask(FakeUpdate(), FakeContext(["hola"]))
            update = FakeUpdate()
            await main._ask(update, FakeContext(["hola"]))

        self.assertIn("límite", update.effective_message.replies[-1].lower())

    async def test_ask_without_key_reports_configuration(self):
        with mock.patch.object(config, "AI_API_KEY", ""):
            update = FakeUpdate()
            await main._ask(update, FakeContext(["hola"]))
        self.assertIn("no está configurada", update.effective_message.replies[-1])

    async def test_store_and_prompt_uses_force_reply(self):
        context = FakeContext()
        update = FakeUpdate()
        await interactive.store_and_prompt(
            update, context, interactive.AskInput("precio", "¿Qué producto buscas?")
        )
        self.assertEqual(context.user_data[interactive.PENDING_KEY]["command"], "precio")
        self.assertIn("¿Qué producto buscas?", update.effective_message.replies[0])
        self.assertIsInstance(update.effective_message.reply_markups[0], telegram.ForceReply)

    async def test_dispatch_guided_skill_prompts_with_force_reply(self):
        update = FakeUpdate()
        context = FakeContext([])
        entry = skills.list_skills()["autos"]
        await main._dispatch(update, context, entry)
        self.assertEqual(context.user_data[interactive.PENDING_KEY]["command"], "autos")
        self.assertIsInstance(update.effective_message.reply_markups[0], telegram.ForceReply)


if __name__ == "__main__":
    unittest.main()
