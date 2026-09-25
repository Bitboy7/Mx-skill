# Guía: autos usados/seminuevos confiables

Skill `mx-used-car-search`. Busca autos usados en anuncios públicos de
Seminuevos.com y los ordena con un **índice de confianza** para compra/reventa.
Disponible en el bot como `/autos`.

## Qué puedes hacer

- Buscar por **marca**, **modelo** y **estado/ciudad**.
- Filtrar por **presupuesto**, **año mínimo** y **kilometraje máximo**.
- Priorizar anuncios de **agencia (dealer)** sobre particulares.
- Ver un **índice de confianza** (0-100) por anuncio, con notas de anomalías
  (precio muy por debajo del mercado, km/año alto, etc.) y la **mediana de precio**.

## Comandos del bot

| Comando | Qué hace |
| --- | --- |
| `/autos <marca> [modelo] [en <estado>]` | Lista autos usados confiables |

Ejemplos:

- `/autos nissan sentra`
- `/autos toyota corolla en jalisco`

## Ejemplos (CLI)

```bash
npx -y @nomadamas/k-skill@0 exec mx-used-car-search scripts/mx_used_car_search.py -- \
  --marca nissan --modelo sentra --limit 8

npx -y @nomadamas/k-skill@0 exec mx-used-car-search scripts/mx_used_car_search.py -- \
  --marca nissan --estado jalisco --precio-max 200000 --anio-min 2018
```

## Cómo se calcula la confianza

Heurística de anuncio (no es una inspección mecánica):

- **Antigüedad**: más nuevo suma; >15 años resta.
- **Kilometraje por año**: ≤12,000 km/año suma; >30,000 km/año resta.
- **Precio vs. mediana** del conjunto: cerca de la mediana suma; muy por debajo
  (−30 %) marca alerta de verificación; muy por encima resta.
- **Agencia (dealer)**: suma.

## Precauciones y límites

- **Verifica el NIV en REPUVE** y los adeudos de tenencia/refrendo antes de pagar.
  La skill solo enlaza esas fuentes oficiales; no verifica legalmente el vehículo.
- La estructura del sitio puede cambiar; si no se parsean anuncios se reporta el
  fallo explícitamente.
- Precios y disponibilidad cambian; confirma en el anuncio original.
- No realiza compra, apartado ni pagos.
