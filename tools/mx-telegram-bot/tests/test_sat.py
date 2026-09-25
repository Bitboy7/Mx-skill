"""Pruebas de los handlers SAT del bot, sin red ni Telegram real.

Se ejecuta con el Python del bot (o con cualquier Python 3.10+):
  python -m unittest discover -s tests -p "test_*.py"
"""

import pathlib
import sys
import unittest
from unittest import mock

import _telegram_stub

_telegram_stub.install()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import bot.interactive as interactive  # noqa: E402
import bot.main as main  # noqa: E402
import bot.runner as runner  # noqa: E402
import bot.skills as skills  # noqa: E402


class FakeContext:
    def __init__(self, args, user_data=None):
        self.args = args
        self.user_data = user_data if user_data is not None else {}


def _payload_for(args):
    action = args[args.index("--action") + 1]
    if action == "factura":
        return {
            "action": "factura",
            "uuid": "11111111-1111-1111-1111-111111111111",
            "rfc_emisor": "AAA010101AAA",
            "rfc_receptor": "BBB010101BBB",
            "total": "1250.30",
            "estado": "Vigente",
            "vigente": True,
            "es_cancelable": "Cancelable sin aceptacion",
            "codigo_estatus": "S - Comprobante obtenido satisfactoriamente.",
        }
    if action == "69b":
        return {
            "action": "69b",
            "rfc": args[args.index("--rfc") + 1],
            "encontrado": True,
            "situacion": "Presunto",
            "detalle": "El RFC aparece en el listado 69-B.",
        }
    if action == "constancia":
        return {
            "action": "constancia",
            "encontrado": True,
            "rfc": args[args.index("--rfc") + 1],
            "id_cif": args[args.index("--id-cif") + 1],
            "url": "https://siat.sat.gob.mx/app/qr/x",
            "datos": {
                "RFC": "AAA010101AAA",
                "Nombre, Denominacion o Razon Social": "ACME SA DE CV",
                "Regimenes": [
                    {
                        "RegimenFiscal": "601 - General de Ley Personas Morales",
                        "Fecha de alta": "2010-01-01",
                    }
                ],
            },
        }
    if action == "catalogo":
        if "--clave" in args:
            return {
                "action": "catalogo",
                "tipo": args[args.index("--tipo") + 1],
                "etiqueta": "Regimen fiscal",
                "clave": args[args.index("--clave") + 1],
                "descripcion": "General de Ley Personas Morales",
                "encontrado": True,
            }
        return {
            "action": "catalogo",
            "tipo": args[args.index("--tipo") + 1],
            "etiqueta": "Clave de producto/servicio",
            "encontrado": True,
            "resultados": [{"clave": "43231500", "descripcion": "Software funcional"}],
        }
    raise AssertionError(f"accion inesperada: {action}")


def fake_runner():
    calls = []

    async def _run_skill(skill_id, args, timeout=45.0):
        calls.append((skill_id, list(args)))
        return _payload_for(list(args))

    return _run_skill, calls


class SatHandlerTests(unittest.IsolatedAsyncioTestCase):
    def test_registry_exposes_sat_commands(self):
        registered = skills.list_skills()
        for command in ("sat_factura", "sat_69b", "sat_constancia", "sat_catalogo"):
            self.assertIn(command, registered)
            self.assertEqual(registered[command].skill_id, "sat-consulta")

    def test_sat_keyboard_has_options(self):
        keyboard = interactive.sat_keyboard()
        flat = " ".join(button for row in keyboard.args[0] for button in row)
        for command in ("/sat_factura", "/sat_69b", "/sat_constancia", "/sat_catalogo", "/menu"):
            self.assertIn(command, flat)

    def test_menu_keyboard_shows_sat_in_first_row(self):
        keyboard = interactive.menu_keyboard()
        rows = keyboard.args[0]
        self.assertIn("/sat", " ".join(rows[0]))
        self.assertLessEqual(len(rows), 8, "el menú debe ser compacto para no truncarse")

    def test_bot_commands_include_sat_and_skills(self):
        commands = {c.command for c in main._bot_commands()}
        self.assertIn("sat", commands)
        self.assertIn("sat_factura", commands)
        self.assertIn("clima", commands)

    async def test_sat_factura_formats_result(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["sat_factura"].handler(
                None, FakeContext(["11111111-1111-1111-1111-111111111111", "AAA010101AAA", "BBB010101BBB", "1250.30"])
            )

        self.assertIn("CFDI VIGENTE", text)
        self.assertIn("1250.30", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "sat-consulta")
        self.assertEqual(args[:2], ["--action", "factura"])

    async def test_sat_factura_accepts_single_line_from_resume(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            await skills.list_skills()["sat_factura"].handler(
                None, FakeContext(["11111111-1111-1111-1111-111111111111 AAA010101AAA BBB010101BBB 1250.30"])
            )

        skill_id, args = calls[0]
        self.assertIn("1250.30", args)

    async def test_sat_factura_asks_when_missing(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["sat_factura"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.command, "sat_factura")

    async def test_sat_69b_reports_listado(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["sat_69b"].handler(None, FakeContext(["aaa010101aaa"]))

        self.assertIn("69-B", text)
        self.assertIn("Presunto", text)
        skill_id, args = calls[0]
        self.assertEqual(args, ["--action", "69b", "--rfc", "AAA010101AAA", "--json"])

    async def test_sat_69b_asks_when_missing(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["sat_69b"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.command, "sat_69b")

    async def test_sat_constancia_parses_qr_url(self):
        fake, calls = fake_runner()
        url = "https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3=012345678_AAA010101AAA"
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["sat_constancia"].handler(None, FakeContext([url]))

        self.assertIn("Constancia", text)
        self.assertIn("601 - General de Ley Personas Morales", text)
        skill_id, args = calls[0]
        self.assertEqual(args[:2], ["--action", "constancia"])
        self.assertIn("012345678", args)
        self.assertIn("AAA010101AAA", args)

    async def test_sat_constancia_asks_when_missing(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["sat_constancia"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.command, "sat_constancia")

    async def test_sat_catalogo_uses_clave_when_code_like(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["sat_catalogo"].handler(None, FakeContext(["regimen", "601"]))

        self.assertIn("601", text)
        self.assertIn("General de Ley Personas Morales", text)
        skill_id, args = calls[0]
        self.assertIn("--clave", args)
        self.assertNotIn("--buscar", args)

    async def test_sat_catalogo_uses_buscar_for_text(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["sat_catalogo"].handler(None, FakeContext(["producto", "software"]))

        self.assertIn("Software funcional", text)
        skill_id, args = calls[0]
        self.assertIn("--buscar", args)
        self.assertNotIn("--clave", args)

    async def test_sat_catalogo_rejects_unknown_type(self):
        text = await skills.list_skills()["sat_catalogo"].handler(None, FakeContext(["nope", "x"]))
        self.assertIn("Catalogo no soportado", text)

    async def test_sat_catalogo_asks_when_missing(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["sat_catalogo"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.command, "sat_catalogo")


if __name__ == "__main__":
    unittest.main()
