# Guía de precios de la canasta básica (PROFECO)

## Qué puedes hacer

- Costo de la canasta básica (24 productos) por tienda, estado y zona (México).
- Listado ordenado de menor a mayor costo.

## Entradas

- `--top N`: resultados (por defecto 10).
- `--estado`: filtro por estado (acepta alias como `CDMX`, `Edomex` o `NL`).

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec precios-canasta scripts/precios_canasta.py -- --estado "Jalisco"
```

## Fuentes

- Reporte semanal "Productos de Primera Necesidad" (PDF): https://qqph.profeco.gob.mx
- Índice de reportes por año: https://qqph.profeco.gob.mx/api/archivos/2026
- Portal "Quién es Quién en los Precios": https://www.profeco.gob.mx/precios/canasta/home.aspx

## Precauciones

- La antigua API `api.datos.gob.mx/v1/precio.canasta.basica` fue retirada; el portal vigente publica un PDF semanal que el helper descarga y parsea.
- El reporte solo publica los 5 precios más altos y 5 más bajos por zona, no el universo completo de tiendas.
- Precios promedio por región y fecha; varían entre tiendas.
