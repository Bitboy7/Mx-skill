# MX Real Estate

## What this skill does

Busca **inmuebles en renta o venta en México** usando **Inmuebles24**: lee los
anuncios que el portal sirve en `window.__PRELOADED_STATE__` (`listStore.listPostings`)
y devuelve título, tipo, operación, precio, recámaras, baños, superficie, zona,
inmobiliaria y enlace. Sin API key.

Mercado Libre Inmuebles ya no permite búsqueda pública (HTTP 403 desde abril de
2025), por eso se usa Inmuebles24 como fuente principal.

## When to use

- "Busca departamentos en renta en Polanco"
- "Casas en venta en Guadalajara"
- "¿Qué rentas hay en la Roma?"

## When not to use

- Para cerrar un trato o pagar: la operación se hace con el anunciante/plataforma (el skill es de solo consulta).

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key ni sesión.

## Inputs

- `--q`: búsqueda libre (ej. "departamento polanco", "casa acapulco").
- `--tipo`: `venta` (por defecto) o `renta`.
- `--limit`: resultados (por defecto 5).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-real-estate scripts/mx_real_estate.py -- --q "departamento polanco" --tipo renta --limit 5
```

## Official surfaces

- Inmuebles24: `https://www.inmuebles24.com/{tipo}-en-{operacion}-en-{zona}.html`
- Portales alternativos (solo referencia): Vivanuncios, Propiedades.com.

## Done when

- Se listaron inmuebles con precio, zona y enlace.
- Se indicó el total en la página y el tipo (venta/renta).

## Failure modes

- **Sin resultados para el tipo pedido**: se reintenta con inmuebles en general y se anota en `nota`.
- **Zona no reconocida**: Inmuebles24 redirige a resultados generales; se avisa en `nota`.
- **HTTP no-200 / red caída**: mensaje con enlaces a los portales alternativos.
- Nombres de zona ambiguos: se corrigen con un mapa de alias (p. ej. `acapulco` → `acapulco-de-juarez`).

## Notes

- Skill de solo consulta. Los precios son los publicados en los anuncios.
- No se comparten datos personales del usuario con los anunciantes.
