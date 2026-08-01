# Mercado Libre Search

## What this skill does

Busca **productos en Mercado Libre México (MLM)** usando la **API pública documentada** (`api.mercadolibre.com/sites/MLM/search`), sin API key. Devuelve título, precio, descuento, vendedor, ubicación y enlace.

## When to use

- "Busca audífonos bluetooth en Mercado Libre"
- "¿Cuánto cuesta una cafetera en Mercado Libre México?"
- "Compara precios de un iPhone en MLM"

## When not to use

- Para comprar directamente: la compra se hace en el sitio web oficial (el skill es de solo consulta).
- Cuando la red del usuario está detrás de una IP de datacenter (el API puede bloquear con 403).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--q`: búsqueda.
- `--limit`: resultados (por defecto 5).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mercado-libre-search scripts/mercado_libre_search.py -- --q "audifonos bluetooth" --limit 5
```

## Official surface

- API pública: `https://api.mercadolibre.com/sites/MLM/search?q=<query>`
- Portal público: `https://listado.mercadolibre.com.mx/<query>`

## Done when

- Se listaron productos con precio y enlace.
- Se indicó el total de resultados disponibles.

## Failure modes

- **HTTP 403**: el API está bloqueado para IPs de datacenter/cloud (desde IP residencial funciona). En ese caso se remite al portal público `listado.mercadolibre.com.mx`.
- Sin resultados para la búsqueda.

## Notes

- Skill de solo consulta; no realiza compras.
- Los precios son los publicados en el momento de la búsqueda.
