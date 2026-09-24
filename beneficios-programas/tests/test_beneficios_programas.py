import contextlib
import importlib.util
import io
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "beneficios-programas" / "scripts" / "beneficios_programas.py"
SPEC = importlib.util.spec_from_file_location("beneficios_programas", MODULE_PATH)
beneficios_programas = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(beneficios_programas)


class BeneficiosHelperTests(unittest.TestCase):
    def test_strip_accents(self):
        self.assertEqual(beneficios_programas.strip_accents("Jóvenes"), "Jovenes")
        self.assertEqual(beneficios_programas.strip_accents("Pensión"), "Pension")

    def test_search_is_accent_insensitive(self):
        results = beneficios_programas.search_programs("pension")
        names = [p["nombre"] for p in results]
        self.assertTrue(any("Adultas Mayores" in n for n in names))
        self.assertTrue(any("Discapacidad" in n for n in names))

        accented = beneficios_programas.search_programs("jóvenes")
        self.assertTrue(accented, "search with accents should still match")

    def test_search_matches_requisitos_and_perfil(self):
        results = beneficios_programas.search_programs("bachillerato")
        self.assertEqual([p["nombre"] for p in results], ["Beca Benito Juárez"])

    def test_filter_by_categoria(self):
        results = beneficios_programas.search_programs("", categoria="campo y pesca")
        self.assertGreaterEqual(len(results), 3)
        self.assertTrue(all(p["categoria"] == "campo y pesca" for p in results))

    def test_empty_search_returns_full_catalog(self):
        results = beneficios_programas.search_programs("")
        self.assertEqual(len(results), len(beneficios_programas.CATALOG))

    def test_every_program_links_to_the_official_portal(self):
        for program in beneficios_programas.CATALOG:
            self.assertTrue(program["enlace"].startswith(beneficios_programas.PORTAL))
            self.assertTrue(program["requisitos"])

    def test_build_payload_includes_source_and_note(self):
        payload = beneficios_programas.build_payload([], query="x")
        self.assertEqual(payload["modo"], "busqueda")
        self.assertIn("note", payload)
        self.assertIn("Bienestar", payload["source"])

    def test_format_text_lists_requirements_and_link(self):
        results = beneficios_programas.search_programs("pension")
        text = beneficios_programas.format_text(beneficios_programas.build_payload(results, query="pension"))
        self.assertIn("Pensión para el Bienestar", text)
        self.assertIn("Requisitos", text)
        self.assertIn("programasparaelbienestar.gob.mx", text)

    def test_main_query_prints_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            beneficios_programas.main(["pension", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["modo"], "busqueda")
        self.assertTrue(rendered["results"])

    def test_main_accepts_query_flag_used_by_the_bot(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            beneficios_programas.main(["--query", "pension", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["query"], "pension")
        self.assertTrue(rendered["results"])

    def test_main_list_prints_all(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            beneficios_programas.main(["--list", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["modo"], "lista")
        self.assertEqual(len(rendered["results"]), len(beneficios_programas.CATALOG))

    def test_main_requires_query_or_list(self):
        with self.assertRaises(SystemExit):
            beneficios_programas.main([])


if __name__ == "__main__":
    unittest.main()
