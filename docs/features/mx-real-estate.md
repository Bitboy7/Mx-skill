# Guía de búsqueda de inmuebles en México

## Qué puedes hacer

- Buscar inmuebles en renta o venta en México (Inmuebles24).
- Precio, recámaras, baños, superficie, zona, inmobiliaria y enlace.

## Entradas

- `--q`: búsqueda. `--tipo`: `venta` o `renta`. `--limit`.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-real-estate scripts/mx_real_estate.py -- --q "departamento polanco" --tipo renta --limit 5
```

## Superficies

- Inmuebles24: https://www.inmuebles24.com/
- Portales alternativos (solo referencia): Vivanuncios, Propiedades.com

## Precauciones

- Mercado Libre Inmuebles ya no permite búsqueda pública (HTTP 403 desde abril de 2025); por eso se usa Inmuebles24.
- Si no hay resultados del tipo pedido, se reintenta con inmuebles en general y se avisa en `nota`.
- La operación de renta/venta se cierra con el anunciante. Solo consulta.
