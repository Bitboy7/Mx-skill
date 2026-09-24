# Guía de precios de gasolina en México

## Qué puedes hacer

- Encontrar las gasolineras más baratas cerca de una ubicación en México.
- Comparar precios de Magna (regular), Premium o Diésel.
- Filtrar por radio y ordenar por precio.

## Primero necesitas

- Python 3 (solo biblioteca estándar).
- Internet. La publicación de la CRE es pública y no requiere API key; se llama directo desde la máquina del usuario (no usa `k-skill-proxy`).

## Entradas

- Ubicación: `--place "colonia, ciudad, estado"` o `--lat/--lon`.
- Combustible: `--fuel regular|premium|diesel` (por defecto `regular`).
- Radio: `--radius-km` (por defecto 10). Resultados: `--limit` (por defecto 5).

## Flujo básico

1. Preguntar siempre la ubicación al usuario (no se estima).
2. Resolver la ubicación (geocodificación pública Open-Meteo o coordenadas).
3. Descargar el catálogo (`/publicaciones/places`) y los precios (`/publicaciones/prices`).
4. Combinar por `place_id`, calcular distancia (haversine) y filtrar por radio.
5. Ordenar por precio del combustible elegido y resumir 3–5 estaciones.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec gas-prices-mx scripts/gas_prices.py -- --place "Cuauhtemoc, Ciudad de Mexico"
npx -y @nomadamas/k-skill@0 exec gas-prices-mx scripts/gas_prices.py -- --lat 19.4326 --lon -99.1332 --fuel premium --radius-km 15 --limit 3
```

## Fuente oficial

- Precios CRE: https://publicacionexterna.azurewebsites.net/publicaciones/prices
- Catálogo CRE: https://publicacionexterna.azurewebsites.net/publicaciones/places
- Portal oficial de la CRE: https://www.gob.mx/cre

## Precauciones

- La publicación puede fallar temporalmente (5xx o conexión rechazada); reintentar y, si persiste, indicar el portal oficial.
- La publicación no incluye calle/colonia/municipio; se ofrece un enlace de mapa por estación.
- Es un skill de solo consulta; no compra ni reserva nada.
