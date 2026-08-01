# Melate Results

## What this skill does

Consulta los **resultados oficiales de la Lotería Nacional de México** (loterianacional.gob.mx): el sorteo más reciente de Melate, Revancha, Revanchita y otras bolsas (Chispazo, Tris, Progol, Mayor, etc.), junto con el número de sorteo, la fecha y la bolsa acumulada. También compara los números del usuario contra el último sorteo de Melate.

## When to use

- "¿Cuáles salieron en el Melate?"
- "Revísame mis números del Melate: 6 14 21 32 40 49"
- "¿En qué quedó la bolsa de Melate?"
- "¿Cuál fue el resultado del Chispazo?"

## When not to use

- Para comprar boletos, reclamar premios o saber el detalle exacto de premios por categoría (usa el verificador oficial `Home/BuscadorBoleto`).
- Para sorteos históricos: esta página oficial solo publica los resultados más recientes.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar, sin dependencias externas).
- Sin API key ni inicio de sesión.

## Inputs

- Juego a consultar (opcional): `--game melate|revancha|chispazo|tris|...`
- Para verificar: seis números (y el adicional si se desea).

## Workflow

### 1. Latest results (default)

```bash
npx -y @nomadamas/k-skill@0 exec melate-results scripts/melate_results.py -- latest
```

### 2. Filter by game

```bash
npx -y @nomadamas/k-skill@0 exec melate-results scripts/melate_results.py -- latest --game melate
```

### 3. Check the user's numbers against the latest Melate

```bash
npx -y @nomadamas/k-skill@0 exec melate-results scripts/melate_results.py -- check --numbers "6 14 21 32 40 49"
```

Ejemplo de salida (2026-07-31, sorteo 4246):

```json
{
  "game": "Melate",
  "sorteo": "4246",
  "draw_date": "31/07/2026",
  "draw_numbers": "06 14 21 32 40 49-45",
  "user_numbers": [6, 14, 21, 32, 40, 49],
  "matching_numbers": [6, 14, 21, 32, 40, 49],
  "match_count": 6,
  "official_checker": "https://www.loterianacional.gob.mx/Home/BuscadorBoleto"
}
```

## Official surface

- Resultados: `https://www.loterianacional.gob.mx/Home/Resultados` (HTML con paneles por juego, se parsea el DOM server-rendered).
- Verificador oficial de boletos: `https://www.loterianacional.gob.mx/Home/BuscadorBoleto`.

## Responding

- Resume el sorteo, la fecha, los números ganadores y la bolsa acumulada.
- En `check`, reporta cuántos números coincidieron y conecta con el verificador oficial para confirmar el premio exacto (el premio por categoría solo lo determina Lotería Nacional).
- No inventes categorías de premios; la tabla oficial puede cambiar por sorteo.

## Done when

- Se obtuvo el sorteo más reciente con números, fecha y bolsa.
- En `check`, se reportaron los números coincidentes y se dio el enlace oficial de verificación.
- Si el HTML cambió y no se encontró ningún panel, se explica el fallo y se da la URL oficial como alternativa.

## Failure modes

- El sitio oficial cambia el HTML de los paneles y el parser no encuentra `Número ganador` / `Sorteo` / `Fecha`.
- El sitio está caído, devuelve 5xx o bloquea la petición (los resultados no dejan de existir; se enlaza la URL oficial).
- Un sorteo se acaba de celebrar y la página aún no publica los números (la actualización suele ser minutos después del cierre).

## Notes

- Skill de solo consulta (lookup). No compra boletos ni reclama premios.
- No almacena ningún número del usuario.
