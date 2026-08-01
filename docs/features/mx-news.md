# Guía de noticias de México (Google News RSS)

## Qué puedes hacer

- Portada de noticias de México en español.
- Búsqueda por palabra clave.

## Entradas

- Comando `top` o `search --q "<palabra clave>"`.
- `--limit`: número de resultados.

## Ejemplos

```bash
npx -y @nomadamas/k-skill@0 exec mx-news scripts/mx_news.py -- top --limit 10
npx -y @nomadamas/k-skill@0 exec mx-news scripts/mx_news.py -- search --q "economia mexico"
```

## Fuente

- Google News RSS (es-MX): https://news.google.com/rss

## Precauciones

- Los enlaces son de Google News; el usuario decide si abre el artículo.
- Solo consulta; no se scrapea medios individuales.
