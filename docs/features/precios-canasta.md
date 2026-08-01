# Guía de precios de la canasta básica (PROFECO)

## Qué puedes hacer

- Costo de la canasta básica por tienda y estado (México).
- Listado ordenado de menor a mayor costo.

## Entradas

- `--top N`: resultados (por defecto 10).
- `--estado`: filtro por estado.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec precios-canasta scripts/precios_canasta.py -- --estado "Jalisco"
```

## Fuentes

- API pública PROFECO/datos.gob.mx: https://api.datos.gob.mx/v1/precio.canasta.basica
- Portal "Quién es Quién en los Precios": https://www.profeco.gob.mx/precios/canasta/home.aspx

## Precauciones

- La API de datos.gob.mx puede estar temporalmente fuera de servicio (503).
- Precios promedio por región y fecha; varían entre tiendas.
