"""Pruebas del logging del bot y del manejo de errores transitorios."""

import logging
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

import _telegram_stub

_telegram_stub.install()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import bot.errors as errors  # noqa: E402
import bot.logging_setup as logging_setup  # noqa: E402
import bot.main as main  # noqa: E402
import bot.runner as runner  # noqa: E402


class FakeMessage:
    def __init__(self):
        self.replies = []

    async def reply_text(self, *args, **kwargs):
        self.replies.append((args, kwargs))


class FakeUpdate:
    def __init__(self, with_message=True):
        self.effective_message = FakeMessage() if with_message else None


class FakeContext:
    def __init__(self, error):
        self.error = error


class ErrorClassificationTests(unittest.TestCase):
    def test_is_transient_for_network_errors(self):
        self.assertTrue(errors.is_transient(errors.NetworkError("down")))
        self.assertTrue(errors.is_transient(errors.TimedOut("slow")))
        self.assertTrue(errors.is_transient(errors.RetryAfter("wait")))

    def test_is_transient_false_for_other_errors(self):
        self.assertFalse(errors.is_transient(ValueError("boom")))
        self.assertFalse(errors.is_transient(None))

    def test_describe_includes_type_and_message(self):
        self.assertEqual(errors.describe(errors.NetworkError("down")), "NetworkError: down")
        self.assertEqual(errors.describe(None), "desconocido")


class LoggingSetupTests(unittest.TestCase):
    def test_configure_logging_returns_bot_logger(self):
        logger = logging_setup.configure_logging("INFO", "")
        self.assertEqual(logger.name, "mx-bot")

    def test_configure_logging_silences_noisy_loggers(self):
        logging_setup.configure_logging("INFO", "")
        for name in ("httpx", "httpcore", "telegram"):
            self.assertEqual(logging.getLogger(name).level, logging.WARNING)

    def test_configure_logging_respects_debug_level(self):
        logging_setup.configure_logging("DEBUG", "")
        self.assertEqual(logging.getLogger().level, logging.DEBUG)
        # Aun en DEBUG, los loggers ruidosos se quedan en WARNING.
        self.assertEqual(logging.getLogger("httpx").level, logging.WARNING)


class OnErrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_transient_error_logs_warning_without_replying(self):
        update = FakeUpdate()
        with self.assertLogs("mx-bot", level="WARNING") as captured:
            await main._on_error(update, FakeContext(errors.NetworkError("All connection attempts failed")))

        self.assertEqual(update.effective_message.replies, [])
        self.assertTrue(any("transitorio" in line.lower() for line in captured.output))

    async def test_unexpected_error_logs_error_and_replies(self):
        update = FakeUpdate()
        with self.assertLogs("mx-bot", level="ERROR") as captured:
            await main._on_error(update, FakeContext(ValueError("boom")))

        self.assertEqual(len(update.effective_message.replies), 1)
        self.assertTrue(any("error no controlado" in line.lower() for line in captured.output))

    async def test_unexpected_error_without_message_does_not_crash(self):
        with self.assertLogs("mx-bot", level="ERROR"):
            await main._on_error(FakeUpdate(with_message=False), FakeContext(ValueError("boom")))


class RunnerLoggingTests(unittest.IsolatedAsyncioTestCase):
    def _write_script(self, body: str) -> pathlib.Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
        handle.write(body)
        handle.close()
        return pathlib.Path(handle.name)

    async def test_run_skill_logs_success(self):
        script = self._write_script("import json\nprint(json.dumps({'ok': True}))\n")
        try:
            with mock.patch.object(runner, "resolve_script", return_value=script):
                with self.assertLogs("mx-bot.runner", level="INFO") as captured:
                    data = await runner.run_skill("fake-skill", ["--x", "1"])
            self.assertEqual(data, {"ok": True})
            self.assertTrue(any("ok en" in line for line in captured.output))
        finally:
            script.unlink(missing_ok=True)

    async def test_run_skill_logs_failure(self):
        script = self._write_script("import sys\nsys.stderr.write('boom\\n')\nsys.exit(1)\n")
        try:
            with mock.patch.object(runner, "resolve_script", return_value=script):
                with self.assertLogs("mx-bot.runner", level="WARNING") as captured:
                    with self.assertRaises(runner.SkillError):
                        await runner.run_skill("fake-skill", [])
            self.assertTrue(any("falló" in line for line in captured.output))
        finally:
            script.unlink(missing_ok=True)

    def test_summarize_args_truncates(self):
        summary = runner._summarize_args(["a" * 100, "b"])
        self.assertLessEqual(len(summary.split(" ")[0]), 40)


if __name__ == "__main__":
    unittest.main()
