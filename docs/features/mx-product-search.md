# Guía de búsqueda y comparación de precios en México

## Qué puedes hacer

- Buscar un producto y comparar precios entre varias tiendas mexicanas.
- Ver, por tienda, título, marca, precio, precio original, descuento, rating (si aplica) y enlace.

## Tiendas soportadas

- **Liverpool** (`liverpool.com.mx`): HTML del buscador.
- **Chedraui** (`chedraui.com.mx`) y **OfficeMax** (`officemax.com.mx`): API pública VTEX.

## Entradas

- `--q`: búsqueda (requerido). `--limit`: resultados por tienda. `--tiendas`: lista separada por coma.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-product-search scripts/mx_product_search.py -- --q "audifonos bluetooth" --limit 5
npx -y @nomadamas/k-skill@0 exec mx-product-search scripts/mx_product_search.py -- --q "iphone" --tiendas Liverpool,Chedraui
```

## Fuentes

- Liverpool: https://www.liverpool.com.mx/tienda?s=<query>
- Chedraui: https://www.chedraui.com.mx/api/catalog_system/pub/products/search/?ft=<query>
- OfficeMax: https://www.officemax.com.mx/api/catalog_system/pub/products/search/?ft=<query>

## Precauciones

- Mercado Libre dejó de permitir búsqueda pública (HTTP 403); Walmart, Soriana, Sanborns y Amazon bloquean el scraping automatizado.
- La salida se agrupa por tienda (`por_tienda`); `errores` lista las tiendas que fallaron.
- Solo consulta; la compra se hace en cada tienda.
- Si una tienda cambia su endpoint o layout, actualizar su entrada en `STORES` (`mx_product_search.py`).
