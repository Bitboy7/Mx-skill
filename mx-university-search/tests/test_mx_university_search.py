import contextlib
import importlib.util
import io
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-university-search" / "scripts" / "mx_university_search.py"
SPEC = importlib.util.spec_from_file_location("mx_university_search", MODULE_PATH)
mx_university_search = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx_university_search)


class UniversitySearchHelperTests(unittest.TestCase):
    def test_strip_accents(self):
        self.assertEqual(mx_university_search.strip_accents("México"), "Mexico")
        self.assertEqual(mx_university_search.strip_accents("pública"), "publica")

    def test_search_by_university_name(self):
        results = mx_university_search.search_universities("UNAM")
        self.assertEqual(len(results), 1)
        self.assertIn("UNAM", results[0]["nombre"])

    def test_search_by_career_returns_multiple(self):
        results = mx_university_search.search_universities("medicina")
        self.assertGreaterEqual(len(results), 10)
        self.assertTrue(all(any("Medicina" in c for c in u["carreras"]) for u in results))

    def test_search_is_accent_insensitive(self):
        self.assertTrue(mx_university_search.search_universities("publica", tipo="pública"))

    def test_filter_by_tipo(self):
        results = mx_university_search.search_universities("", tipo="privada")
        self.assertGreaterEqual(len(results), 5)
        self.assertTrue(all(u["tipo"] == "privada" for u in results))

    def test_filter_by_estado(self):
        results = mx_university_search.search_universities("", estado="Jalisco")
        self.assertGreaterEqual(len(results), 2)
        self.assertTrue(all("Jalisco" in u["estado"] for u in results))

    def test_empty_search_returns_full_catalog(self):
        results = mx_university_search.search_universities("")
        self.assertEqual(len(results), len(mx_university_search.CATALOG))

    def test_every_entry_has_site_and_careers(self):
        for uni in mx_university_search.CATALOG:
            self.assertTrue(uni["sitio"].startswith("https://"))
            self.assertTrue(uni["carreras"])
            self.assertIn(uni["tipo"], ("pública", "privada"))

    def test_build_payload_includes_source_and_note(self):
        payload = mx_university_search.build_payload([], query="x")
        self.assertEqual(payload["modo"], "busqueda")
        self.assertIn("note", payload)
        self.assertIn("universidades", payload["source"])

    def test_format_text_lists_careers_and_site(self):
        results = mx_university_search.search_universities("UNAM")
        text = mx_university_search.format_text(mx_university_search.build_payload(results, query="UNAM"))
        self.assertIn("UNAM", text)
        self.assertIn("Medicina", text)
        self.assertIn("https://www.unam.mx", text)

    def test_main_query_prints_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            mx_university_search.main(["medicina", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["modo"], "busqueda")
        self.assertTrue(rendered["results"])

    def test_main_accepts_query_flag_used_by_the_bot(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            mx_university_search.main(["--query", "UNAM", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["query"], "UNAM")

    def test_main_list_prints_all(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            mx_university_search.main(["--list", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["modo"], "lista")
        self.assertEqual(len(rendered["results"]), len(mx_university_search.CATALOG))

    def test_main_requires_query_or_list(self):
        with self.assertRaises(SystemExit):
            mx_university_search.main([])


if __name__ == "__main__":
    unittest.main()
