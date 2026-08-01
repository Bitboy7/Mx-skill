# MX Real Estate

## What this skill does

Busca **inmuebles en renta o venta en México** usando la **API pública de Mercado Libre Inmuebles** (categorías de renta/venta), y documenta los portales alternativos (Vivanuncios, Inmuebles24, Propiedades.com) como superficies oficiales de referencia.

## When to use

- "Busca departamentos en renta en Polanco"
- "Casas en venta en Guadalajara"
- "¿Qué rentas hay cerca de la Roma?"

## When not to use

- Para cerrar un trato o pagar: la operación se hace con el anunciante/plataforma (el skill es de solo consulta).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- `--q`: búsqueda (ej. "departamento polanco").
- `--tipo`: `venta` (por defecto) o `renta`.
- `--limit`: resultados (por defecto 5).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-real-estate scripts/mx_real_estate.py -- --q "departamento polanco" --tipo renta --limit 5
```

## Official surfaces

- API pública: `https://api.mercadolibre.com/sites/MLM/search` (categoría Inmuebles).
- Portales alternativos: Vivanuncios, Inmuebles24, Propiedades.com.

## Done when

- Se listaron inmuebles con precio, zona y enlace.
- Se indicó el total de resultados y el tipo (venta/renta).

## Failure modes

- **HTTP 403** de Mercado Libre desde IP de datacenter: remitir a los portales alternativos.
- Precios/atributos faltantes en el anuncio: se omiten sin inventar.
- Los portales alternativos tienen protección anti-bot; se documentan, no se automatizan.

## Notes

- Skill de solo consulta. Los precios son los publicados en los anuncios.
- No se comparten datos personales del usuario con los anunciantes.
