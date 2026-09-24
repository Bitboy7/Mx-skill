# Guía de búsqueda de productos en México (Liverpool)

## Qué puedes hacer

- Buscar productos y precios en Liverpool México.
- Comparar precio, precio original, descuento, marca y rating, con enlace.

## Entradas

- `--q`: búsqueda. `--limit`: resultados.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-product-search scripts/mx_product_search.py -- --q "audifonos bluetooth" --limit 5
```

## Fuentes

- Buscador: https://www.liverpool.com.mx/tienda?s=<query>

## Precauciones

- Mercado Libre dejó de permitir búsqueda pública (HTTP 403 desde abril de 2025); por eso se usa Liverpool.
- Solo consulta; la compra se hace en liverpool.com.mx.
- Si Liverpool cambia sus `data-testid`, actualizar los selectores del helper.
