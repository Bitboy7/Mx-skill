"""Pruebas de los handlers de las skills MX nuevas, sin red ni Telegram real.

Se ejecuta con el Python del bot (o con cualquier Python 3.10+):
  python -m unittest discover -s tests -p "test_*.py"
"""

import asyncio
import pathlib
import sys
import unittest
from unittest import mock

# La instalación de python-telegram-bot no es necesaria para probar los
# handlers: se usa un stub mínimo de `telegram`.
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


PAYLOADS = {
    "mx-air-quality": {
        "place": {"name": "Ciudad de Mexico"},
        "medido_en": "2026-09-23T12:00",
        "calidad": {
            "indice_us_aqi": 64,
            "categoria": "Moderada",
            "pm2_5_ug_m3": 10.2,
            "pm10_ug_m3": 10.4,
            "recomendacion": "Aceptable; las personas muy sensibles pueden notar molestias.",
        },
    },
    "mx-holiday-calendar": {
        "results": [
            {
                "fecha": "2026-11-16",
                "nombre_local": "Dia de la Revolucion",
                "tipos": ["Oficial"],
                "dias_faltantes": 54,
            }
        ]
    },
    "mx-restroom-nearby": {
        "radio_m": 1000,
        "results": [
            {
                "nombre": "Sanitarios Publicos",
                "distancia_km": 0.174,
                "costo": "De pago",
                "acceso": "Publico",
                "mapa": "https://www.openstreetmap.org/node/1",
            }
        ],
    },
    "compranet-search": {
        "source": "LicitIA Abierto (CC BY 4.0) sobre datos públicos de Compras MX",
        "results": [
            {
                "numero": "aa-06-hjo-006hjo001-n-46-2026",
                "nombre": "SERVICIO DE SOFTWARE",
                "dependencia": "006HJO - BANCO DEL BIENESTAR",
                "tipo": "ADJUDICACION DIRECTA",
                "estatus": "ADJUDICADO",
                "url_oficial": "https://comprasmx.buengobierno.gob.mx/sitiopublico/#/detalle/x",
            }
        ],
    },
    "beneficios-programas": {
        "portal": "https://www.programasparaelbienestar.gob.mx",
        "results": [
            {
                "nombre": "Pensión para el Bienestar de las Personas Adultas Mayores",
                "categoria": "adultos mayores",
                "apoyo": "Apoyo económico bimestral.",
                "monto": "Consultar monto vigente en el enlace oficial.",
                "requisitos": ["Tener 65 años en adelante", "Residir en México"],
                "enlace": "https://www.programasparaelbienestar.gob.mx/programas/adultos-mayores/",
            }
        ],
    },
    "mx-job-search": {
        "source": "Vacantes Digitales (API pública, sin API key)",
        "official_links": {"vacantes_digitales": "https://vacantesdigitales.com/vacantes"},
        "results": [
            {
                "puesto": "Desarrollador C++",
                "empresa": "Phinder",
                "modalidad": "Presencial",
                "tipo_empleo": "Tiempo completo",
                "ubicacion": "Ciudad de México",
                "url": "https://www.linkedin.com/feed/update/urn:li:activity:1",
            }
        ],
    },
    "mx-university-search": {
        "results": [
            {
                "nombre": "Universidad Nacional Autónoma de México (UNAM)",
                "tipo": "pública",
                "ciudad": "Ciudad de México",
                "estado": "Ciudad de México",
                "carreras": ["Medicina", "Derecho", "Ingeniería en Computación"],
                "sitio": "https://www.unam.mx",
            }
        ],
    },
    "mx-product-search": {
        "source": "Liverpool Mexico (datos publicos del buscador)",
        "results": [
            {
                "titulo": "Audífonos True Wireless Galaxy Buds",
                "marca": "SAMSUNG",
                "precio_mxn": 799,
                "precio_original_mxn": 999,
                "descuento_pct": 20,
                "rating": 4.5,
                "link": "https://www.liverpool.com.mx/tienda/pdp/audifonos/1182610185",
            }
        ],
    },
    "mx-real-estate": {
        "source": "Inmuebles24 (datos publicos de los anuncios)",
        "results": [
            {
                "titulo": "Departamento en Polanco",
                "precio": "$9,000,000 MXN",
                "dormitorios": "3",
                "banos": "2",
                "superficie_m2": "264 m²",
                "ubicacion": "Polanco, Miguel Hidalgo, Ciudad de México",
                "link": "https://www.inmuebles24.com/propiedades/clasificado/abc-1.html",
            }
        ],
    },
}


def fake_runner():
    calls = []

    async def _run_skill(skill_id, args, timeout=45.0):
        calls.append((skill_id, list(args)))
        return PAYLOADS[skill_id]

    return _run_skill, calls


class NewSkillHandlerTests(unittest.IsolatedAsyncioTestCase):
    def test_registry_exposes_new_commands_and_real_helpers(self):
        registered = skills.list_skills()
        for command, skill_id in [
            ("aire", "mx-air-quality"),
            ("feriado", "mx-holiday-calendar"),
            ("banos", "mx-restroom-nearby"),
            ("licitaciones", "compranet-search"),
            ("bienestar", "beneficios-programas"),
            ("empleo", "mx-job-search"),
            ("universidades", "mx-university-search"),
            ("precio", "mx-product-search"),
            ("inmuebles", "mx-real-estate"),
        ]:
            self.assertIn(command, registered)
            self.assertEqual(registered[command].skill_id, skill_id)
            script = runner.resolve_script(skill_id)
            self.assertTrue(script.is_file(), f"missing helper for {skill_id}: {script}")

    async def test_aire_formats_air_quality(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["aire"].handler(None, FakeContext(["Monterrey"]))

        self.assertIn("Calidad del aire en Ciudad de Mexico", text)
        self.assertIn("64 (Moderada)", text)
        self.assertIn("PM2.5", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-air-quality")
        self.assertIn("--place", args)
        self.assertIn("--json", args)

    async def test_aire_uses_shared_location_when_no_place(self):
        fake, calls = fake_runner()
        user_data = {"mx_location": {"lat": 19.43, "lon": -99.16, "timestamp": __import__("time").time(), "approx_km": 1.1}}
        with mock.patch.object(runner, "run_skill", new=fake):
            await skills.list_skills()["aire"].handler(None, FakeContext([], user_data))

        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-air-quality")
        self.assertIn("--lat", args)
        self.assertIn("--json", args)

    async def test_aire_asks_for_place_when_missing(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["aire"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.kind, "place")

    async def test_feriado_defaults_to_current_year(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["feriado"].handler(None, FakeContext([]))

        self.assertIn("Días feriados de este año", text)
        self.assertIn("2026-11-16", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-holiday-calendar")
        self.assertEqual(args, ["--json"])

    async def test_feriado_supports_year_and_next(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            await skills.list_skills()["feriado"].handler(None, FakeContext(["2027"]))
            await skills.list_skills()["feriado"].handler(None, FakeContext(["proximos"]))

        self.assertEqual(calls[0][1], ["--year", "2027", "--json"])
        self.assertEqual(calls[1][1], ["--next", "--json"])

    async def test_banos_formats_results(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["banos"].handler(None, FakeContext(["Zocalo CDMX"]))

        self.assertIn("Baños públicos cerca de Zocalo CDMX", text)
        self.assertIn("Sanitarios Publicos", text)
        self.assertIn("openstreetmap.org/node/1", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-restroom-nearby")
        self.assertIn("--json", args)

    async def test_banos_empty_result_message(self):
        async def empty_skill(skill_id, args, timeout=45.0):
            return {"radio_m": 1000, "results": []}

        with mock.patch.object(runner, "run_skill", new=empty_skill):
            text = await skills.list_skills()["banos"].handler(None, FakeContext(["Nada"]))

        self.assertIn("No se encontraron baños públicos", text)

    async def test_licitaciones_formats_results(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["licitaciones"].handler(None, FakeContext(["software"]))

        self.assertIn("Licitaciones para 'software'", text)
        self.assertIn("SERVICIO DE SOFTWARE", text)
        self.assertIn("aa-06-hjo-006hjo001-n-46-2026", text)
        self.assertIn("comprasmx.buengobierno.gob.mx", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "compranet-search")
        self.assertEqual(args[:2], ["--query", "software"])
        self.assertIn("--json", args)

    async def test_licitaciones_asks_for_query(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["licitaciones"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.kind, "text")

    async def test_bienestar_formats_program(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["bienestar"].handler(None, FakeContext(["pension"]))

        self.assertIn("Pensión para el Bienestar", text)
        self.assertIn("65 años", text)
        self.assertIn("programasparaelbienestar.gob.mx", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "beneficios-programas")
        self.assertEqual(args[:2], ["--query", "pension"])

    async def test_bienestar_todos_uses_list_mode(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            await skills.list_skills()["bienestar"].handler(None, FakeContext(["todos"]))

        self.assertEqual(calls[0][1], ["--list", "--json"])

    async def test_bienestar_asks_for_topic(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["bienestar"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.kind, "text")

    async def test_empleo_formats_vacancies(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["empleo"].handler(None, FakeContext(["python"]))

        self.assertIn("Vacantes para 'python'", text)
        self.assertIn("Desarrollador C++", text)
        self.assertIn("Phinder", text)
        self.assertIn("linkedin.com", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-job-search")
        self.assertEqual(args[:2], ["--query", "python"])
        self.assertIn("--json", args)

    async def test_empleo_asks_for_query(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["empleo"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.kind, "text")

    async def test_universidades_formats_results(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["universidades"].handler(None, FakeContext(["medicina"]))

        self.assertIn("Universidades para 'medicina'", text)
        self.assertIn("UNAM", text)
        self.assertIn("Medicina", text)
        self.assertIn("https://www.unam.mx", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-university-search")
        self.assertEqual(args[:2], ["--query", "medicina"])

    async def test_universidades_todos_uses_list_mode(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            await skills.list_skills()["universidades"].handler(None, FakeContext(["todos"]))

        self.assertEqual(calls[0][1], ["--list", "--json"])

    async def test_universidades_asks_for_query(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["universidades"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.kind, "text")

    async def test_precio_formats_products(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["precio"].handler(None, FakeContext(["audifonos"]))

        self.assertIn("Precios: audifonos", text)
        self.assertIn("Galaxy Buds", text)
        self.assertIn("799", text)
        self.assertIn("liverpool.com.mx", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-product-search")
        self.assertEqual(args[:2], ["--q", "audifonos"])

    async def test_precio_groups_by_store(self):
        async def multi_store(skill_id, args, timeout=45.0):
            return {
                "query": "audifonos",
                "por_tienda": {
                    "Liverpool": [{"tienda": "Liverpool", "titulo": "Galaxy Buds", "precio_mxn": 799, "link": "https://www.liverpool.com.mx/x"}],
                    "Chedraui": [{"tienda": "Chedraui", "titulo": "Aiwa Bluetooth", "precio_mxn": 372.06, "link": "https://www.chedraui.com.mx/y"}],
                    "OfficeMax": [],
                },
                "errores": {"OfficeMax": "HTTP 503"},
            }

        with mock.patch.object(runner, "run_skill", new=multi_store):
            text = await skills.list_skills()["precio"].handler(None, FakeContext(["audifonos"]))

        self.assertIn("Liverpool", text)
        self.assertIn("Chedraui", text)
        self.assertIn("Aiwa Bluetooth", text)
        self.assertIn("$372.06", text)
        self.assertNotIn("OfficeMax", text.split("Sin datos de")[0])
        self.assertIn("Sin datos de: OfficeMax", text)

    async def test_precio_asks_for_query(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["precio"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.kind, "text")

    async def test_inmuebles_formats_results(self):
        fake, calls = fake_runner()
        with mock.patch.object(runner, "run_skill", new=fake):
            text = await skills.list_skills()["inmuebles"].handler(None, FakeContext(["renta", "polanco"]))

        self.assertIn("Inmuebles (renta): polanco", text)
        self.assertIn("Departamento en Polanco", text)
        self.assertIn("3 rec.", text)
        skill_id, args = calls[0]
        self.assertEqual(skill_id, "mx-real-estate")
        self.assertEqual(args[:2], ["--q", "polanco"])
        self.assertIn("--tipo", args)

    async def test_inmuebles_asks_for_query(self):
        with self.assertRaises(interactive.AskInput) as ctx:
            await skills.list_skills()["inmuebles"].handler(None, FakeContext([]))
        self.assertEqual(ctx.exception.kind, "text")


if __name__ == "__main__":
    unittest.main()
