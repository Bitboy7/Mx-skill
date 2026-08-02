# MX Sports Results

## What this skill does

Consulta datos del **fútbol mexicano** usando la API pública de **ESPN** (sin API key): marcadores por fecha, tabla de posiciones del torneo actual y lista de equipos de la **Liga BBVA MX (Liga MX)** y de la **Liga de Expansión MX**.

## When to use

- "¿Cómo va la tabla de la Liga MX?"
- "¿En qué posición está el América?"
- "¿Qué partidos hubo ayer en la Liga MX?"
- "Dame la tabla de la Liga de Expansión"

## When not to use

- Para otros deportes mexicanos (béisbol LMB, básquetbol LNBP): esta skill solo cubre fútbol por ahora (sin fuente pública sin clave verificada; ver Failure modes).
- Para datos históricos muy antiguos o alineaciones/minuto a minuto.

## Prerequisites

- Internet y `python3` (solo biblioteca estándar).
- Sin API key ni inicio de sesión.

## Inputs

- `--league`: `mex.1` (Liga MX, por defecto) o `mex.2` (Liga de Expansión).
- `--date`: fecha `YYYY-MM-DD` para marcadores (por defecto: hoy, UTC).
- `--team`: nombre o abreviatura del equipo (sin distinguir acentos, p. ej. "america" encuentra "América").

## Workflow

### 1. Tabla de posiciones (por defecto)

```bash
npx -y @nomadamas/k-skill@0 exec mx-sports-results scripts/mx_sports.py -- standings
```

### 2. Posición de un equipo concreto

```bash
npx -y @nomadamas/k-skill@0 exec mx-sports-results scripts/mx_sports.py -- standings --team america
```

### 3. Marcadores de una fecha

```bash
npx -y @nomadamas/k-skill@0 exec mx-sports-results scripts/mx_sports.py -- scoreboard --date 2026-07-31
npx -y @nomadamas/k-skill@0 exec mx-sports-results scripts/mx_sports.py -- scoreboard --date 2026-07-31 --team guadalajara
```

### 4. Otra liga

```bash
npx -y @nomadamas/k-skill@0 exec mx-sports-results scripts/mx_sports.py -- standings --league mex.2
npx -y @nomadamas/k-skill@0 exec mx-sports-results scripts/mx_sports.py -- teams --league mex.2
```

## Official surface

- Marcadores: `https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard?dates=YYYYMMDD`
- Posiciones: `https://site.web.api.espn.com/apis/v2/sports/soccer/{league}/standings`
- Equipos: `https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/teams`

## Responding

- En posiciones, resume el torneo (p. ej. Apertura 2026) y muestra la tabla ordenada: posición, equipo, PJ, G, E, P, GF/GC y puntos. Con `--team`, muestra solo la fila de ese equipo.
- En marcadores, resume partido a partido: estado (Final/En juego/Programado), local, visitante, marcador y ganador si terminó.
- "Hoy/ayer" siempre se traduce a una fecha absoluta `YYYY-MM-DD` (UTC) antes de ejecutar.
- No inventes partidos ni posiciones; si la fuente no devuelve datos, explícalo y enlaza el sitio oficial.

## Done when

- Se obtuvo la tabla de posiciones del torneo actual con PJ, G/E/P y puntos.
- O se obtuvieron los marcadores de la fecha pedida con estado y marcador.
- El filtro por equipo (si se pidió) dejó solo sus partidos/fila.

## Failure modes

- La API de ESPN cambia la estructura o responde 5xx (los resultados no dejan de existir; se enlaza el sitio oficial de la liga).
- Fecha sin partidos (por ejemplo, día de descanso o fecha futura lejana): la API devuelve lista vacía y el script lo reporta.
- Equipo no encontrado: verificar el nombre/abreviatura reales (p. ej. `teams --league`).
- Torneo recién iniciado: la tabla puede estar incompleta o no publicada aún.
- **Otros deportes mexicanos (LMB béisbol, LNBP básquetbol) no están cubiertos**: no se encontró una fuente pública sin clave estable (Sofascore bloquea con 403, TheSportsDB sin clave útil, sitios oficiales LMB/LNBP son SPAs). No intentar scrapear en su lugar.

## Notes

- Skill de solo consulta (lookup). No almacena datos del usuario.
- Fuente pública agregada (ESPN); para lo oficial se remite a la Liga BBVA MX y la Liga de Expansión.
