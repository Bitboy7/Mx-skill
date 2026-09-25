# Skills MX del bot

Índice de las **skills mexicanas que usa el bot de Telegram**
(`tools/mx-telegram-bot`). Es solo un índice de referencia: los archivos de cada
skill viven en la **raíz del repo** (layout plano requerido por el CLI, el
plugin y los tests de skills).

- Bot: [`tools/mx-telegram-bot`](../tools/mx-telegram-bot/README.md)
- Cómo añadir una skill al bot: [`tools/mx-telegram-bot/README.md`](../tools/mx-telegram-bot/README.md)

## Comandos y skills

| Comando | Skill | Qué hace | Fuente pública |
| --- | --- | --- | --- |
| `/clima <ciudad>` | `mx-weather` | Clima actual y pronóstico | Open-Meteo (ref. CONAGUA/SMN) |
| `/aire <ciudad>` | `mx-air-quality` | Calidad del aire (PM2.5, PM10, US AQI) | Open-Meteo Air Quality (ref. SEDEMA/SEMARNAT) |
| `/noticias [query]` | `mx-news` | Portada o búsqueda de noticias | RSS de Google News (es-MX) |
| `/melate [números]` | `melate-results` | Resultados de la Lotería Nacional / verificar números | loterianacional.gob.mx |
| `/cp <cp>` | `mx-zipcode-search` | Colonias/estado de un código postal | SEPOMEX (fuentes públicas) |
| `/rfc <rfc>` | `sat-rfc-lookup` | Valida la estructura de un RFC | SAT |
| `/ecobici <lugar>` | `ecobici-cdmx` | Estaciones de Ecobici CDMX | GBFS oficial |
| `/cine [funciones]` | `cine-mx` | Cartelera y funciones | Cinemex / Cinépolis |
| `/candidatos <nombre>` | `comision-ine` | Candidaturas del INE | "Conóceles" |
| `/canasta [estado]` | `precios-canasta` | Precios de la canasta básica | PROFECO |
| `/ruta <origen> a <destino>` | `mx-transit-route` | Ruta auto/caminando/bici | OSRM + Open-Meteo |
| `/gasolina <lugar>` | `gas-prices-mx` | Gasolineras más baratas | CRE (publicación oficial) |
| `/precio <producto>` | `mx-product-search` | Búsqueda y comparación de precios | Liverpool, Chedraui, OfficeMax |
| `/inmuebles [renta\|venta] <q>` | `mx-real-estate` | Inmuebles en México | Inmuebles24 |
| `/envio <guía>` | `delivery-tracking-mx` | Seguimiento de paquete | Estafeta |
| `/futbol [equipo\|jornada]` | `mx-sports-results` | Liga MX / Liga de Expansión | API pública de ESPN |
| `/feriado [año\|proximos]` | `mx-holiday-calendar` | Días feriados oficiales | Nager.Date |
| `/banos <lugar>` | `mx-restroom-nearby` | Baños públicos cerca | OpenStreetMap / Overpass |
| `/licitaciones <palabra>` | `compranet-search` | Licitaciones y contrataciones públicas | Compras MX vía LicitIA |
| `/bienestar [tema\|todos]` | `beneficios-programas` | Programas para el Bienestar | Portal oficial |
| `/empleo <puesto\|skill>` | `mx-job-search` | Vacantes de empleo (tecnología/LATAM) | API pública Vacantes Digitales |
| `/universidades <carrera\|universidad>` | `mx-university-search` | Universidades de México y sus carreras | Catálogo curado + enlaces oficiales |

## Ubicación compartida 📍

Estas skills usan la ubicación que compartas con el bot (📎 → Ubicación):
`/clima`, `/ecobici`, `/gasolina`, `/aire`, `/banos` y `/ruta a <destino>`.

## Guías por skill

- [mx-weather](../docs/features/mx-weather.md)
- [mx-air-quality](../docs/features/mx-air-quality.md)
- [mx-news](../docs/features/mx-news.md)
- [melate-results](../docs/features/melate-results.md)
- [mx-zipcode-search](../docs/features/mx-zipcode-search.md)
- [sat-rfc-lookup](../docs/features/sat-rfc-lookup.md)
- [ecobici-cdmx](../docs/features/ecobici-cdmx.md)
- [cine-mx](../docs/features/cine-mx.md)
- [comision-ine](../docs/features/comision-ine.md)
- [precios-canasta](../docs/features/precios-canasta.md)
- [mx-transit-route](../docs/features/mx-transit-route.md)
- [gas-prices-mx](../docs/features/gas-prices-mx.md)
- [mx-product-search](../docs/features/mx-product-search.md)
- [mx-real-estate](../docs/features/mx-real-estate.md)
- [delivery-tracking-mx](../docs/features/delivery-tracking-mx.md)
- [mx-sports-results](../mx-sports-results/instruction.md)
- [mx-holiday-calendar](../docs/features/mx-holiday-calendar.md)
- [mx-restroom-nearby](../docs/features/mx-restroom-nearby.md)
- [compranet-search](../docs/features/compranet-search.md)
- [beneficios-programas](../docs/features/beneficios-programas.md)
- [mx-job-search](../docs/features/mx-job-search.md)
- [mx-university-search](../docs/features/mx-university-search.md)
