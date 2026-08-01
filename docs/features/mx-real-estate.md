# Guía de búsqueda de inmuebles en México

## Qué puedes hacer

- Buscar inmuebles en renta o venta en México (Mercado Libre Inmuebles).
- Precio, zona, atributos y enlace.

## Entradas

- `--q`: búsqueda. `--tipo`: `venta` o `renta`. `--limit`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-real-estate scripts/mx_real_estate.py -- --q "departamento polanco" --tipo renta --limit 5
```

## Superficies

- API pública: https://api.mercadolibre.com/sites/MLM/search (Inmuebles)
- Portales alternativos: Vivanuncios, Inmuebles24, Propiedades.com

## Precauciones

- Desde IPs de datacenter el API puede dar 403; remitir a los portales alternativos.
- La operación de renta/venta se cierra con el anunciante.
- Solo consulta.
