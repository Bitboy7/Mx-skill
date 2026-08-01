# Guía de búsqueda en Mercado Libre México

## Qué puedes hacer

- Buscar productos en Mercado Libre México (MLM).
- Comparar precios, descuentos, vendedor y enlaces.

## Entradas

- `--q`: búsqueda. `--limit`: resultados.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mercado-libre-search scripts/mercado_libre_search.py -- --q "audifonos bluetooth" --limit 5
```

## Fuentes

- API pública: https://api.mercadolibre.com/sites/MLM/search
- Portal: https://listado.mercadolibre.com.mx/

## Precauciones

- Desde IPs de datacenter el API puede dar 403; desde IP residencial funciona.
- Solo consulta; la compra se hace en el sitio oficial.
