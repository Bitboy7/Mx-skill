import contextlib
import importlib.util
import io
import json
import pathlib
import unittest
import urllib.parse
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-job-search" / "scripts" / "mx_job_search.py"
SPEC = importlib.util.spec_from_file_location("mx_job_search", MODULE_PATH)
mx_job_search = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx_job_search)


API_RESPONSE = {
    "data": [
        {
            "id": 5640,
            "title": "Desarrollador C++ Microservicios - Presencial - CDMX",
            "position": "Desarrollador C++",
            "company": {"name": "Phinder", "slug": "phinder"},
            "job_category": "desarrollo",
            "experience": "junior",
            "job_location_type": "ONSITE",
            "employment_type": "FULL_TIME",
            "address_locality": "Ciudad de México",
            "address_country": "MX",
            "salary": None,
            "date_posted_iso": "2026-06-11T17:14:45.636Z",
            "skills": ["C++", "STL", "REST APIs"],
            "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:1",
        }
    ],
    "pagination": {"page": 1, "limit": 5, "total": 1, "pages": 1},
}


class JobSearchHelperTests(unittest.TestCase):
    def test_build_params_includes_query_and_source(self):
        params = mx_job_search.build_params("python", 5)
        self.assertEqual(params["q"], "python")
        self.assertEqual(params["limit"], 5)
        self.assertEqual(params["page"], 1)
        self.assertEqual(params["source"], mx_job_search.SOURCE)

    def test_build_params_adds_optional_filters(self):
        params = mx_job_search.build_params("data", 10, page=2, category="data", experience="senior", location_type="remoto")
        self.assertEqual(params["page"], 2)
        self.assertEqual(params["category"], "data")
        self.assertEqual(params["experience"], "senior")
        self.assertEqual(params["location_type"], "remoto")

    def test_build_params_omits_empty_filters(self):
        params = mx_job_search.build_params("python", 5)
        self.assertNotIn("category", params)
        self.assertNotIn("experience", params)
        self.assertNotIn("location_type", params)

    def test_normalize_item_translates_and_maps(self):
        row = mx_job_search.normalize_item(API_RESPONSE["data"][0])
        self.assertEqual(row["puesto"], "Desarrollador C++")
        self.assertEqual(row["empresa"], "Phinder")
        self.assertEqual(row["modalidad"], "Presencial")
        self.assertEqual(row["tipo_empleo"], "Tiempo completo")
        self.assertEqual(row["ubicacion"], "Ciudad de México")
        self.assertEqual(row["habilidades"], ["C++", "STL", "REST APIs"])
        self.assertTrue(row["url"].startswith("https://www.linkedin.com"))

    def test_normalize_item_translates_telecommute_and_contract(self):
        row = mx_job_search.normalize_item(
            {"position": "Dev", "job_location_type": "TELECOMMUTE", "employment_type": "CONTRACT"}
        )
        self.assertEqual(row["modalidad"], "Remoto")
        self.assertEqual(row["tipo_empleo"], "Contrato")

    def test_fetch_jobs_builds_query_and_parses_data(self):
        captured = {}

        def fake(url, timeout=30):
            captured["url"] = url
            return API_RESPONSE

        with mock.patch.object(mx_job_search, "http_get_json", side_effect=fake):
            results = mx_job_search.fetch_jobs("python", 3, category="data")

        params = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
        self.assertEqual(params["q"], ["python"])
        self.assertEqual(params["limit"], ["3"])
        self.assertEqual(params["category"], ["data"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["puesto"], "Desarrollador C++")

    def test_build_payload_always_includes_official_links(self):
        payload = mx_job_search.build_payload("python", [])
        self.assertIn("portal_del_empleo", payload["official_links"])
        self.assertNotIn("notice", payload)

    def test_build_payload_with_error_adds_notice(self):
        payload = mx_job_search.build_payload("python", [], error="timeout")
        self.assertIn("notice", payload)
        self.assertIn("timeout", payload["notice"])

    def test_main_accepts_args_used_by_the_bot(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_job_search, "fetch_jobs", return_value=[]),
        ):
            mx_job_search.main(["--query", "python", "--limit", "5", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["query"], "python")

    def test_main_degrades_to_official_links_on_network_error(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_job_search, "fetch_jobs", side_effect=OSError("down")),
        ):
            mx_job_search.main(["python", "--json"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["results"], [])
        self.assertIn("notice", rendered)
        self.assertIn("vacantes_digitales", rendered["official_links"])

    def test_main_requires_query(self):
        with self.assertRaises(SystemExit):
            mx_job_search.main([])

    def test_main_rejects_out_of_range_limit(self):
        with self.assertRaises(SystemExit):
            mx_job_search.main(["python", "--limit", "0"])
        with self.assertRaises(SystemExit):
            mx_job_search.main(["python", "--limit", "51"])


if __name__ == "__main__":
    unittest.main()
