# MX Product Search

## What this skill does

Busca y **compara precios de un producto en varias tiendas mexicanas**. Devuelve,
por tienda, título, marca, precio, precio original, descuento, rating (cuando la
tienda lo publica) y enlace. Sin API key ni sesión.

Tiendas soportadas:

- **Liverpool** (`liverpool.com.mx`): HTML server-rendered con tarjetas de producto.
- **Chedraui** (`chedraui.com.mx`) y **OfficeMax** (`officemax.com.mx`): API pública
  de catálogo VTEX (`/api/catalog_system/pub/products/search/`).

Mercado Libre dejó de permitir búsqueda pública (HTTP 403 desde abril de 2025) y
Walmart, Soriana, Sanborns y Amazon bloquean el scraping automatizado, por eso no
se incluyen.

## When to use

- "Busca audífonos bluetooth"
- "¿Cuánto cuesta una cafetera?"
- "Compara precios de un iPhone"

## When not to use

- Para comprar directamente: la compra se hace en cada tienda (el skill es de solo consulta).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key ni sesión.

## Inputs

- `--q`: búsqueda (requerido).
- `--limit`: resultados **por tienda** (por defecto 5, máximo 20).
- `--tiendas`: tiendas separadas por coma (por defecto todas: `Liverpool,Chedraui,OfficeMax`).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-product-search scripts/mx_product_search.py -- --q "audifonos bluetooth" --limit 5
npx -y @nomadamas/k-skill@0 exec mx-product-search scripts/mx_product_search.py -- --q "iphone" --tiendas Liverpool,Chedraui
```

## Official surface

- Liverpool: `https://www.liverpool.com.mx/tienda?s=<query>`
- Chedraui: `https://www.chedraui.com.mx/api/catalog_system/pub/products/search/?ft=<query>`
- OfficeMax: `https://www.officemax.com.mx/api/catalog_system/pub/products/search/?ft=<query>`

## Done when

- Se listaron productos con precio y enlace, agrupados por tienda.
- Se indicaron los resultados por tienda y las tiendas sin datos (si hubo).

## Failure modes

- **Sin tarjetas de producto (Liverpool)**: el parser devuelve vacío; actualizar los `data-testid`.
- **HTTP no-200 / red caída**: la tienda se reporta en `errores` y las demás siguen devolviendo resultados.
- **Sin resultados en ninguna tienda**: mensaje con el detalle de errores.
- **Cambios de layout/endpoint de una tienda**: actualizar su entrada en `STORES` dentro de `mx_product_search.py`.

## Notes

- Skill de solo consulta; no realiza compras.
- Los precios son los publicados en el momento de la búsqueda y pueden variar.
- La comparación es a nivel de resultados de búsqueda por tienda (no hay matching exacto de SKU entre tiendas).
