"""Pruebas del handler de autos usados, sin red ni Telegram real."""

import pathlib
import sys
import unittest
from unittest import mock

import _telegram_stub

_telegram_stub.install()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import bot.interactive as interactive  # noqa: E402
import bot.runner as runner  # noqa: E402
import bot.skills as skills  # noqa: E402


class FakeContext:
    def __init__(self, args, user_data=None):
        self.args = args
        self.user_data = user_data if user_data is not None else {}


PAYLOAD = {
    "source": "Seminuevos.com (anuncios publicos, sin API key)",
    "precio_mediana_mxn": 300000,
    "results": [
        {
            "titulo": "Nissan Sentra 2023",
            "url": "https://www.seminuevos.com/vehicle/x/111",
            "precio_mxn": 299000,
            "anio": 2023,
            "km": 21000,
            "ubicacion": "Monterrey",
            "confianza": 90,
            "confianza_nivel": "Alta",
            "notas": [],
        }
    ],
}


def fake_runner(payload=None):
    calls = []

    async def _run_skill(skill_id, args, timeout=45.0):
        calls.append((skill_id, list(args)))
        return payload if payload is not None else PAYLOAD

    return _run_skill, calls


class UsedCarHandlerTests(unittest.IsolatedAsyncioTestCase):
    def test_registry_exposes_autos(self):
        registered = skills.list_skills()
        self.assertIn("autos", registered)
        self.assertEqual(registered["autos"].skill_id, "mx-used-car-search")

    def test_menu_includes_autos(self):
        keyboard = interactive.menu_keyboard()
        flat = " ".join(button for row in keyboard.args[0] for button in row)
        self.assertIn("/autos", flat)

    async def test_autos_formats_results(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["autos"].handler(None, FakeContext(["nissan", "sentra"]))

        self.assertIn("Nissan Sentra 2023", text)
        self.assertIn("$299,000", text)
        self.assertIn("confianza Alta", text)
        self.assertIn("Mediana del mercado", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-used-car-search")
        self.assertIn("--marca", args)
        self.assertIn("nissan", args)
        self.assertIn("--modelo", args)
        self.assertIn("sentra", args)

    async def test_autos_parses_estado_with_en(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["autos"].handler(
                None, FakeContext(["toyota", "corolla", "en", "jalisco"])
            )

        self.assertIn("en jalisco", text)
        skill_id, args = calls[0]
        self.assertIn("--estado", args)
        self.assertIn("jalisco", args)

    async def test_autos_asks_when_missing(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["autos"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.command, "autos")

    async def test_autos_empty_result_message(self):
        fake, _ = fake_runner({"results": [], "notice": "Ningun anuncio cumple los filtros."})
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["autos"].handler(None, FakeContext(["nissan"]))
        self.assertIn("Sin resultados", text)


if __name__ == "__main__":
    unittest.main()
