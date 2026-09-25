"""Pruebas de la capa de IA (sin red real)."""

import io
import json
import pathlib
import sys
import unittest
import urllib.error
from unittest import mock

import _telegram_stub

_telegram_stub.install()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import bot.ai as ai  # noqa: E402
import bot.config as config  # noqa: E402


class FakeResponse:
    def __init__(self, payload):
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _http_error(code, body):
    return urllib.error.HTTPError(
        url="https://api.test/v1/chat/completions",
        code=code,
        msg="Bad Request",
        hdrs=None,
        fp=io.BytesIO(json.dumps(body).encode("utf-8")),
    )


class AiLayerTests(unittest.TestCase):
    def setUp(self):
        self._patch = mock.patch.multiple(
            config,
            AI_API_KEY="test-key",
            AI_BASE_URL="https://api.test/v1",
            AI_MODEL="gpt-6-luna",
            AI_TEMPERATURE=None,
        )
        self._patch.start()
        self.addCleanup(self._patch.stop)

    def test_call_chat_omits_temperature_by_default(self):
        captured = {}

        def fake_urlopen(req, timeout=60):
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return FakeResponse({"choices": [{"message": {"content": "ok"}}]})

        with mock.patch.object(ai.urllib.request, "urlopen", side_effect=fake_urlopen):
            content = ai._call_chat([{"role": "user", "content": "hola"}])

        self.assertEqual(content, "ok")
        self.assertNotIn("temperature", captured["body"])

    def test_call_chat_includes_temperature_when_configured(self):
        config.AI_TEMPERATURE = 0
        captured = {}

        def fake_urlopen(req, timeout=60):
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return FakeResponse({"choices": [{"message": {"content": "ok"}}]})

        with mock.patch.object(ai.urllib.request, "urlopen", side_effect=fake_urlopen):
            ai._call_chat([{"role": "user", "content": "hola"}])

        self.assertEqual(captured["body"]["temperature"], 0)

    def test_call_chat_surfaces_api_error_message(self):
        error = _http_error(400, {"error": {"message": "'temperature' does not support 0"}})
        with mock.patch.object(ai.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(RuntimeError) as ctx:
                ai._call_chat([{"role": "user", "content": "hola"}])
        self.assertIn("HTTP 400", str(ctx.exception))
        self.assertIn("temperature", str(ctx.exception))

    def test_extract_json_handles_code_fences(self):
        routed = ai._extract_json('```json\n{"skill": "chat", "text": "hola"}\n```')
        self.assertEqual(routed["skill"], "chat")

    def test_extract_json_rejects_non_json(self):
        with self.assertRaises(ValueError):
            ai._extract_json("no hay json")

    def test_route_query_builds_messages_and_parses(self):
        captured = {}

        def fake_urlopen(req, timeout=60):
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return FakeResponse({"choices": [{"message": {"content": '{"skill": "chat", "text": "ok"}'}}]})

        with mock.patch.object(ai.urllib.request, "urlopen", side_effect=fake_urlopen):
            routed = ai.route_query("consulta libre")

        self.assertEqual(routed, {"skill": "chat", "text": "ok"})
        roles = [m["role"] for m in captured["body"]["messages"]]
        self.assertEqual(roles, ["system", "user"])
        self.assertIn("Catálogo de skills", captured["body"]["messages"][0]["content"])

    def test_route_query_without_key_raises(self):
        config.AI_API_KEY = ""
        with self.assertRaises(RuntimeError):
            ai.route_query("hola")


if __name__ == "__main__":
    unittest.main()
