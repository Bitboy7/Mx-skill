# Guía de precios de gasolina en México

## Qué puedes hacer

- Encontrar las gasolineras más baratas cerca de una ubicación en México.
- Comparar precios de Magna (regular), Premium o Diésel.
- Filtrar por radio y ordenar por precio.

## Primero necesitas

- Python 3 (solo biblioteca estándar).
- Internet. La API de la CRE es pública y no requiere API key; se llama directo desde la máquina del usuario (no usa `k-skill-proxy`).

## Entradas

- Ubicación: `--place "colonia, ciudad, estado"` o `--lat/--lon`.
- Combustible: `--fuel regular|premium|diesel` (por defecto `regular`).
- Radio: `--radius-km` (por defecto 10). Resultados: `--limit` (por defecto 5).
- Cobertura: `--max-pages` (páginas de 100 estaciones; por defecto 20).

## Flujo básico

1. Preguntar siempre la ubicación al usuario (no se estima).
2. Resolver la ubicación (geocodificación pública Open-Meteo o coordenadas).
3. Recorrer páginas del catálogo de la CRE.
4. Calcular distancia (haversine) y filtrar por radio.
5. Ordenar por precio del combustible elegido y resumir 3–5 estaciones.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec gas-prices-mx scripts/gas_prices.py -- --place "Cuauhtemoc, Ciudad de Mexico"
npx -y @nomadamas/k-skill@0 exec gas-prices-mx scripts/gas_prices.py -- --lat 19.4326 --lon -99.1332 --fuel premium --radius-km 15 --limit 3
```

## Fuente oficial

- API pública de precios de la CRE: https://api.datos.gob.mx/v1/precio.gasolina.publico
- Portal oficial de la CRE: https://www.gob.mx/cre

## Precauciones

- La API puede responder 503 temporalmente; reintentar y, si persiste, indicar el portal oficial.
- El catálogo es paginado (100 estaciones por página); si la zona no aparece, subir `--max-pages`.
- Es un skill de solo consulta; no compra ni reserva nada.
