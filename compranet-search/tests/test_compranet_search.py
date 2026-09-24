import contextlib
import importlib.util
import io
import json
import pathlib
import unittest
import urllib.parse
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "compranet-search" / "scripts" / "compranet_search.py"
SPEC = importlib.util.spec_from_file_location("compranet_search", MODULE_PATH)
compranet_search = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(compranet_search)


API_RESPONSE = {
    "success": True,
    "data": [
        {
            "id": "375142",
            "numero_procedimiento": "aa-06-hjo-006hjo001-n-46-2026",
            "nombre_procedimiento": "SERVICIO DE SOFTWARE",
            "dependencia": "006HJO - BANCO DEL BIENESTAR S.N.C.",
            "tipo_procedimiento": "ADJUDICACION DIRECTA",
            "estatus": "ADJUDICADO",
            "anio_ejercicio": 2026,
            "fecha_publicacion": "2026-07-30T13:29:06.000Z",
            "adjudicaciones": 1,
            "licitia_url": "https://licitia.com.mx/adjudicacion/aa-06-hjo-006hjo001-n-46-2026",
            "source_url": "https://comprasmx.buengobierno.gob.mx/sitiopublico/#/detalle/x/procedimiento",
        }
    ],
}


class CompranetSearchHelperTests(unittest.TestCase):
    def test_build_params_includes_filters(self):
        params = compranet_search.build_params("software", 5, year=2026, tipo="LICITACION", estatus="VIGENTE")
        self.assertEqual(params["q"], "software")
        self.assertEqual(params["limit"], 5)
        self.assertEqual(params["anio"], 2026)
        self.assertEqual(params["tipo"], "LICITACION")
        self.assertEqual(params["estatus"], "VIGENTE")

    def test_build_params_omits_empty_filters(self):
        params = compranet_search.build_params("obra", 10)
        self.assertNotIn("anio", params)
        self.assertNotIn("tipo", params)
        self.assertNotIn("estatus", params)

    def test_normalize_item_maps_fields(self):
        row = compranet_search.normalize_item(API_RESPONSE["data"][0])
        self.assertEqual(row["numero"], "aa-06-hjo-006hjo001-n-46-2026")
        self.assertEqual(row["nombre"], "SERVICIO DE SOFTWARE")
        self.assertEqual(row["anio"], 2026)
        self.assertEqual(row["estatus"], "ADJUDICADO")
        self.assertTrue(row["url_oficial"].startswith("https://comprasmx"))

    def test_fetch_licitaciones_builds_query_and_parses_data(self):
        captured = {}

        def fake(url, timeout=30):
            captured["url"] = url
            return API_RESPONSE

        with mock.patch.object(compranet_search, "http_get_json", side_effect=fake):
            results = compranet_search.fetch_licitaciones("software", 3, year=2026)

        params = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
        self.assertEqual(params["q"], ["software"])
        self.assertEqual(params["limit"], ["3"])
        self.assertEqual(params["anio"], ["2026"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nombre"], "SERVICIO DE SOFTWARE")

    def test_fetch_licitaciones_returns_empty_when_success_false(self):
        with mock.patch.object(compranet_search, "http_get_json", return_value={"success": False, "data": []}):
            self.assertEqual(compranet_search.fetch_licitaciones("x", 5), [])

    def test_build_payload_always_includes_official_links(self):
        payload = compranet_search.build_payload("software", [])
        self.assertIn("comprasmx_difusion", payload["official_links"])
        self.assertNotIn("notice", payload)

    def test_build_payload_with_error_adds_notice(self):
        payload = compranet_search.build_payload("software", [], error="timeout")
        self.assertIn("notice", payload)
        self.assertIn("timeout", payload["notice"])

    def test_main_prints_json_with_mocked_fetch(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(compranet_search, "fetch_licitaciones", return_value=compranet_search.build_payload("s", [])["results"]),
        ):
            compranet_search.main(["software", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["query"], "software")
        self.assertIn("official_links", rendered)

    def test_main_degrades_to_official_links_on_network_error(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(compranet_search, "fetch_licitaciones", side_effect=OSError("down")),
        ):
            compranet_search.main(["software", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["results"], [])
        self.assertIn("notice", rendered)
        self.assertIn("comprasmx_datos_abiertos", rendered["official_links"])

    def test_main_accepts_args_used_by_the_bot(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(compranet_search, "fetch_licitaciones", return_value=[]),
        ):
            compranet_search.main(["--query", "software", "--limit", "5", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["query"], "software")

    def test_main_requires_query(self):
        with self.assertRaises(SystemExit):
            compranet_search.main([])

    def test_main_rejects_out_of_range_limit(self):
        with self.assertRaises(SystemExit):
            compranet_search.main(["software", "--limit", "0"])
        with self.assertRaises(SystemExit):
            compranet_search.main(["software", "--limit", "51"])


if __name__ == "__main__":
    unittest.main()
