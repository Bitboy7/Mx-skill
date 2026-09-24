import contextlib
import importlib.util
import io
import json
import pathlib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "mx-product-search" / "scripts" / "mx_product_search.py"
SPEC = importlib.util.spec_from_file_location("mx_product_search", MODULE_PATH)
mx_product_search = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mx_product_search)


def card(product_id, name, brand, price, original=None, rating="4.5"):
    original_html = (
        f'<span data-testid="original"><span class="line-through">$<!-- -->{original}</span></span>'
        if original
        else ""
    )
    return (
        f'<a data-testid="{product_id}-card-card-link" href="/tienda/pdp/{name.replace(" ", "-")}/{product_id}">'
        f'<section data-testid="{product_id}-card">'
        f'<img alt="{name}" src="x.jpg"/>'
        f"<h4>{brand}</h4><h3>{name}</h3>"
        f'<div data-testid="{product_id}-price">'
        f'<span data-testid="discounted"><span>$<!-- -->{price}</span>'
        f'<span><span class="invisible">.</span>00</span></span>'
        f"{original_html}</div>"
        f'<div data-testid="{product_id}-rating"><div aria-label="{rating} stars of 5"></div></div>'
        f"</section></a>"
    )


HTML = "<html><body>" + card("111", "Producto Uno", "MARCA1", 799, 999) + card("222", "Producto Dos", "MARCA2", 499) + "</body></html>"


class ExtractProductsTests(unittest.TestCase):
    def test_parses_product_fields(self):
        products, total = mx_product_search.extract_products(HTML, 5)
        self.assertEqual(total, 2)
        self.assertEqual(len(products), 2)
        first = products[0]
        self.assertEqual(first["titulo"], "Producto Uno")
        self.assertEqual(first["marca"], "MARCA1")
        self.assertEqual(first["precio_mxn"], 799)
        self.assertEqual(first["precio_original_mxn"], 999)
        self.assertEqual(first["descuento_pct"], 20)
        self.assertEqual(first["rating"], 4.5)
        self.assertEqual(first["link"], "https://www.liverpool.com.mx/tienda/pdp/Producto-Uno/111")

    def test_product_without_discount(self):
        products, _ = mx_product_search.extract_products(HTML, 5)
        self.assertEqual(products[1]["precio_mxn"], 499)
        self.assertIsNone(products[1]["precio_original_mxn"])
        self.assertIsNone(products[1]["descuento_pct"])

    def test_respects_limit(self):
        products, total = mx_product_search.extract_products(HTML, 1)
        self.assertEqual(len(products), 1)
        self.assertEqual(total, 2)

    def test_returns_empty_without_cards(self):
        products, total = mx_product_search.extract_products("<html></html>", 5)
        self.assertEqual(products, [])
        self.assertEqual(total, 0)


class BuildUrlTests(unittest.TestCase):
    def test_encodes_query(self):
        url = mx_product_search.build_url("audifonos bluetooth")
        self.assertTrue(url.startswith("https://www.liverpool.com.mx/tienda?s="))
        self.assertIn("s=audifonos+bluetooth", url)


class MainTests(unittest.TestCase):
    def test_main_prints_json(self):
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.object(mx_product_search, "http_get_text", return_value=HTML),
        ):
            mx_product_search.main(["--q", "audifonos", "--limit", "2"])

        rendered = json.loads(stdout.getvalue())
        self.assertEqual(rendered["results"][0]["precio_mxn"], 799)
        self.assertEqual(rendered["query"], "audifonos")

    def test_main_exits_when_no_results(self):
        with mock.patch.object(mx_product_search, "http_get_text", return_value="<html></html>"):
            with self.assertRaises(SystemExit):
                mx_product_search.main(["--q", "nada"])


if __name__ == "__main__":
    unittest.main()
