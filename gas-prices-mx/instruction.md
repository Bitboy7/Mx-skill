# Gas Prices MX

## What this skill does

Encuentra las **gasolineras más baratas cerca de una ubicación en México** usando la **publicación oficial de precios de la CRE** (Comisión Reguladora de Energía), en formato XML y sin API key. Se llaman directo dos endpoints públicos:

- Catálogo de estaciones: `https://publicacionexterna.azurewebsites.net/publicaciones/places`
- Precios por estación: `https://publicacionexterna.azurewebsites.net/publicaciones/prices`

La antigua API `api.datos.gob.mx/v1/precio.gasolina.publico` fue retirada y ya no responde.

- La posición se pide al usuario y se resuelve con geocodificación pública (Open-Meteo) o con coordenadas directas.
- Se combinan catálogo y precios por `place_id`, se calcula distancia (haversine) y se ordena por precio del combustible elegido.
- Combustibles: `regular` (magna, por defecto), `premium`, `diesel`.

## When to use

- "¿Dónde está la gasolinera más barata cerca de Polanco?"
- "Precios de la magna cerca de la colonia Roma"
- "Gasolineras con diésel barato en Monterrey"
- "Dame 5 gasolineras con el precio de la premium más bajo a 5 km"

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
  "source": "https://publicacionexterna.azurewebsites.net/publicaciones/prices",
  "catalogo": "https://publicacionexterna.azurewebsites.net/publicaciones/places",
  "fuel": "regular",
  "anchor": {"query": "Cuauhtemoc, Ciudad de Mexico", "name": "Cuauhtemoc", "admin1": "Ciudad de México", "latitude": 19.43537, "longitude": -99.15271},
  "radius_km": 10,
  "stations_scanned": 13852,
  "stations_in_range": 32,
  "results": [
    {"nombre": "SERVICIO ...", "cre_id": "PL/...", "latitud": 19.43, "longitud": -99.15, "precio": 22.89, "distancia_km": 0.8, "mapa": "https://www.google.com/maps/search/?api=1&query=19.43,-99.15"}
  ]
}
```

## Official surface

- Precios CRE: `https://publicacionexterna.azurewebsites.net/publicaciones/prices`
- Catálogo CRE: `https://publicacionexterna.azurewebsites.net/publicaciones/places`
- Portal oficial de la CRE: `https://www.gob.mx/cre` (sección de precios de gasolinas).

## Responding

- Resume 3–5 estaciones: nombre/razón social, precio del combustible pedido, distancia y enlace a mapa.
- La publicación de la CRE no incluye calle/colonia/municipio; ofrece el enlace de mapa para ubicar la estación.
- Los precios suelen actualizarse cada día.

## Done when

- Se pidió y resolvió la ubicación del usuario.
- Se consultó la publicación pública de la CRE.
- Se encontró al menos 1 gasolinera en el radio con precio para el combustible pedido, o se explicó por qué no (zona sin cobertura / fuente caída).
- Se resumieron los 3–5 resultados más baratos.

## Failure modes

- **HTTP 5xx o conexión rechazada** en `publicacionexterna.azurewebsites.net`: la publicación puede estar caída o con mantenimiento; reintentar y, si persiste, indicar el portal oficial de la CRE.
- Zona sin estaciones en el radio o combustible sin precio registrado.
- Geocodificación sin resultados para el nombre de lugar (pedir otra referencia o coordenadas).

## Notes

- Skill de solo consulta. No compara el precio por marca, no hace reservas ni pide datos personales.
- La fuente es pública y no requiere clave: se llama directo, sin `k-skill-proxy`.
