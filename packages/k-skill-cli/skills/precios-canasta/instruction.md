# Precios Canasta (PROFECO)

## What this skill does

Consulta los **precios de la canasta básica en México** (por tienda y estado) usando la API pública del dataset de **PROFECO** publicado en `datos.gob.mx` ("Precios de la canasta básica"). Sin API key.

## When to use

- "¿Dónde está la canasta básica más barata en Jalisco?"
- "Precios de la canasta en la CDMX"
- "¿Cuánto cuesta la canasta básica en Soriana/Walmart?"

## When not to use

- Para precios por producto individual (no es un catálogo de precios por artículo).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--top N`: mostrar las N canastas más baratas (por defecto 10).
- `--estado`: filtrar por estado (opcional).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec precios-canasta scripts/precios_canasta.py -- --top 10
npx -y @nomadamas/k-skill@0 exec precios-canasta scripts/precios_canasta.py -- --estado "Jalisco"
```

## Official surface

- API pública: `https://api.datos.gob.mx/v1/precio.canasta.basica`
- Portal oficial PROFECO "Quién es Quién en los Precios": `https://www.profeco.gob.mx/precios/canasta/home.aspx`

## Done when

- Se listaron las tiendas con el costo de la canasta básica, ordenadas de menor a mayor.
- Se indicó la fecha de actualización y el estado/región.

## Failure modes

- La API de datos.gob.mx puede estar temporalmente fuera de servicio (HTTP 503); reintentar y, si persiste, remitir al portal de PROFECO.
- El esquema del dataset puede cambiar; el script lee defensivamente y se ajusta en `precios_canasta.py`.

## Notes

- Skill de solo consulta. No compra ni reserva.
- La canasta básica es un promedio del dataset oficial de PROFECO; los precios varían por región y fecha.
