# Gas Prices MX

## What this skill does

Encuentra las **gasolineras más baratas cerca de una ubicación en México** usando la API pública de precios de gasolina y diésel de la **CRE** (Comisión Reguladora de Energía), publicada en datos.gob.mx. No requiere API key ni proxy: es un endpoint público de solo lectura y se llama directo desde la máquina del usuario.

- La posición se pide al usuario y se resuelve con geocodificación pública (Open-Meteo) o con coordenadas directas.
- Se recorren páginas del catálogo de estaciones, se calcula distancia (haversine) y se ordena por precio del combustible elegido.
- Combustibles: `regular` (magna, por defecto), `premium`, `diesel`.

## When to use

- "¿Dónde está la gasolinera más barata cerca de Polanco?"
- "Precios de la magna cerca de la colonia Roma"
- "Gasolineras con diésel barato en Monterrey"
- "Compañía me la gasolina de hoy: dame 5 gasolineras con el precio de la premium más bajo a 5 km"

## Mandatory first question

No se estima la ubicación automáticamente. Antes de buscar, pregunta la posición:

- Pregunta recomendada: `¿Dónde estás? Dame una colonia, ciudad o coordenadas y te busco las gasolineras más baratas cerca.`
- Combustible ambiguo: `¿Magna (regular), Premium o Diésel? Si no lo dices, busco con la magna.`

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key. Fuente pública directa (no va por `k-skill-proxy` porque no requiere clave).

## Inputs

- Ubicación: `--place "colonia, ciudad, estado"` o `--lat/--lon`.
- Combustible: `--fuel regular|premium|diesel` (por defecto `regular`).
- Radio: `--radius-km` (por defecto 10).
- Resultados: `--limit` (por defecto 5).
- Alcance del catálogo: `--max-pages` (páginas de 100 estaciones; por defecto 20 ≈ 2000 estaciones).

## Workflow

### 1. Ask the user for their location first

Siempre preguntar la ubicación antes de buscar.

### 2. Search by place or coordinates

```bash
npx -y @nomadamas/k-skill@0 exec gas-prices-mx scripts/gas_prices.py -- --place "Cuauhtemoc, Ciudad de Mexico"
```

```bash
npx -y @nomadamas/k-skill@0 exec gas-prices-mx scripts/gas_prices.py -- --lat 19.4326 --lon -99.1332 --fuel premium --radius-km 15 --limit 3
```

Ejemplo de salida:

```json
{
  "source": "https://api.datos.gob.mx/v1/precio.gasolina.publico",
  "fuel": "regular",
  "anchor": {"query": "Cuauhtemoc, Ciudad de Mexico", "name": "Cuauhtemoc", "admin1": "Ciudad de México", "latitude": 19.43537, "longitude": -99.15271},
  "radius_km": 10,
  "stations_scanned": 2000,
  "stations_in_range": 32,
  "results": [
    {"razon_social": "...", "calle": "...", "colonia": "...", "municipio": "...", "estado": "...", "precio": 22.89, "distancia_km": 0.8}
  ]
}
```

## Official surface

- API de precios CRE: `https://api.datos.gob.mx/v1/precio.gasolina.publico`
- Portal oficial de la CRE (precios por estación): `https://www.gob.mx/cre` (sección de precios de gasolinas).

## Responding

- Resume 3–5 estaciones: razón social/marca, calle, colonia, municipio/estado, precio del combustible pedido, distancia.
- Indica la fecha de actualización de los precios (suelen actualizarse cada día).
- El catálogo se recorre por páginas; si la zona del usuario no aparece dentro de las páginas escaneadas, sugiere subir `--max-pages` o acotar la ubicación.

## Done when

- Se pidió y resolvió la ubicación del usuario.
- Se consultó la API pública de la CRE.
- Se encontró al menos 1 gasolinera en el radio con precio para el combustible pedido, o se explicó por qué no (zona sin cobertura / API caída).
- Se resumieron los 3–5 resultados más baratos.

## Failure modes

- **HTTP 503 / 5xx** en `api.datos.gob.mx`: la API puede estar caída o con mantenimiento; reintentar y, si persiste, indicar el portal oficial de la CRE.
- Zona sin estaciones en el radio o combustible sin precio registrado en el catálogo escaneado.
- Geocodificación sin resultados para el nombre de lugar (pedir otra referencia o coordenadas).
- El catálogo es paginado (100 por página); un `--max-pages` bajo puede dejar fuera estaciones lejanas.

## Notes

- Skill de solo consulta. No compara el precio por marca, no hace reservas ni pide datos personales.
- La API es pública y no requiere clave: se llama directo, sin `k-skill-proxy`.
