# MX Product Search

## What this skill does

Busca **productos y precios en Liverpool México** leyendo las tarjetas de
producto (`data-testid="<id>-card"`) que el buscador sirve en HTML. Devuelve
título, marca, precio, precio original, descuento, rating y enlace. Sin API key.

Mercado Libre dejó de permitir búsqueda pública (HTTP 403 desde abril de 2025),
por eso se usa Liverpool como fuente principal de productos.

## When to use

- "Busca audífonos bluetooth"
- "¿Cuánto cuesta una cafetera?"
- "Compara precios de un iPhone"

## When not to use

- Para comprar directamente: la compra se hace en liverpool.com.mx (el skill es de solo consulta).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key ni sesión.

## Inputs

- `--q`: búsqueda.
- `--limit`: resultados (por defecto 5).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-product-search scripts/mx_product_search.py -- --q "audifonos bluetooth" --limit 5
```

## Official surface

- Buscador: `https://www.liverpool.com.mx/tienda?s=<query>`

## Done when

- Se listaron productos con precio y enlace.
- Se indicó cuántos resultados trae la primera página.

## Failure modes

- **Sin tarjetas de producto**: mensaje con el enlace del portal para esa búsqueda.
- **HTTP no-200 / red caída**: mensaje con el enlace del portal.
- **Cambios de layout de Liverpool**: si cambian los `data-testid`, el parser devuelve vacío; actualizar los selectores.

## Notes

- Skill de solo consulta; no realiza compras.
- Los precios son los publicados en el momento de la búsqueda.
