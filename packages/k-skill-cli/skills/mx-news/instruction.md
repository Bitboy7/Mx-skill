# MX News

## What this skill does

Busca **noticias de México** (portada o por palabra clave) usando el **feed público RSS de Google News** en español (es-MX). Sin API key.

## When to use

- "¿Cuáles son las noticias de hoy en México?"
- "Busca noticias sobre economía mexicana"
- "¿Qué dice la prensa sobre el peso?"

## When not to use

- Para noticias de un medio específico con suscripción: usar la web de ese medio.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key.

## Inputs

- Comando `top` (portada) o `search --q "<palabra clave>"`.
- `--limit`: número de resultados (por defecto 15).

## Workflow

```bash
npx -y @nomadamas/k-skill@0 exec mx-news scripts/mx_news.py -- top --limit 10
npx -y @nomadamas/k-skill@0 exec mx-news scripts/mx_news.py -- search --q "economia mexico" --limit 5
```

## Done when

- Se obtuvieron y resumieron las noticias (título, fuente, fecha, enlace).
- En búsqueda, los resultados son relevantes a la palabra clave.

## Failure modes

- Google News RSS redirige; el script sigue redirecciones (requiere red abierta).
- Feed vacío o bloqueado (reintentar).

## Notes

- Skill de solo consulta. Los enlaces son de Google News; el usuario decide si abre el artículo.
- No se hace scraping de medios individuales.
