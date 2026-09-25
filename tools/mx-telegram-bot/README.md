# MX Telegram Bot

Bot de Telegram en Python que expone las **skills MX** del repositorio `k-skill` como comandos. Cada comando ejecuta el helper de la skill correspondiente (subproceso) y formatea el JSON en una respuesta legible.

- ✅ Funciona **sin IA**: comandos deterministas que llaman a las skills.
- 🕹️ **Interactivo**: menú de botones (`/menu` o `/start`) para usar los comandos sin escribirlos, y preguntas guiadas cuando un comando necesita parámetros.
- 🤖 Capa de IA **opcional** (`/ask`) que enruta un mensaje libre a la skill correcta (OpenAI u Ollama).

## Requisitos

- Python 3.10+
- Token de bot de Telegram (con `@BotFather`)

## Instalación

```bash
cd tools/mx-telegram-bot
python -m venv .venv
# Windows:  .venv\Scripts\activate      /  Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # y edita TELEGRAM_BOT_TOKEN
```

## Ejecutar (rápido)

La forma más rápida: el script `run.py` crea el venv, instala dependencias, crea `.env` desde `.env.example` y arranca el bot.

```bash
cd tools/mx-telegram-bot
python run.py
```

- Windows: también puedes hacer doble clic en `run.bat`.
- macOS/Linux: `./run.sh`.
- Opciones: `--smoke` (prueba sin Telegram), `--check` (solo verifica el entorno), `--no-install` (no toca dependencias).

### Manual

Si prefieres hacerlo a mano:

```bash
cd tools/mx-telegram-bot
python -m venv .venv
# Windows:  .venv\Scripts\activate      /  Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # y edita TELEGRAM_BOT_TOKEN
python -m bot.main
```

## Comandos

| Comando | Skill interna | Qué hace |
| --- | --- | --- |
| `/clima <ciudad>` | `mx-weather` | Clima actual y pronóstico |
| `/aire <ciudad>` | `mx-air-quality` | Calidad del aire (PM2.5, PM10, US AQI) |
| `/noticias [query]` | `mx-news` | Portada o búsqueda de noticias |
| `/melate [números]` | `melate-results` | Resultados de la Lotería o verifica números |
| `/cp <cp>` | `mx-zipcode-search` | Colonias/estado de un código postal |
| `/rfc <rfc>` | `sat-rfc-lookup` | Valida la estructura de un RFC |
| `/sat_factura <UUID> <RFC emisor> <RFC receptor> <total>` | `sat-consulta` | Estatus de un CFDI (vigente/cancelado) |
| `/sat_69b <rfc>` | `sat-consulta` | RFC en el listado 69-B (EFOS/EDOS) |
| `/sat_constancia <rfc> <id_cif>` | `sat-consulta` | Constancia de Situación Fiscal por QR |
| `/sat_catalogo <tipo> <clave\|texto>` | `sat-consulta` | Catálogos oficiales del SAT |
| `/ecobici <lugar>` | `ecobici-cdmx` | Ecobici CDMX con bicis disponibles |
| `/cine [funciones ...]` | `cine-mx` | Cartelera y funciones (Cinemex) |
| `/candidatos <nombre>` | `comision-ine` | Candidatas y candidatos del INE |
| `/canasta [estado]` | `precios-canasta` | Precios de la canasta básica |
| `/ruta <origen> a <destino>` | `mx-transit-route` | Ruta auto/caminando/bici |
| `/gasolina <lugar>` | `gas-prices-mx` | Gasolineras más baratas cerca |
| `/banos <lugar>` | `mx-restroom-nearby` | Baños públicos cerca (OpenStreetMap) |
| `/precio <producto>` | `mx-product-search` | Búsqueda y comparación de precios (Liverpool, Chedraui, OfficeMax) |
| `/inmuebles [renta\|venta] <q>` | `mx-real-estate` | Inmuebles en México (Inmuebles24) |
| `/envio <guía>` | `delivery-tracking-mx` | Seguimiento de paquete (Estafeta) |
| `/futbol [equipo\|jornada\|expansion]` | `mx-sports-results` | Tabla, posición de un equipo o jornada de la Liga MX |
| `/feriado [año\|proximos]` | `mx-holiday-calendar` | Días feriados oficiales de México |
| `/bienestar [tema\|todos]` | `beneficios-programas` | Programas para el Bienestar: requisitos y enlaces |
| `/licitaciones <palabra>` | `compranet-search` | Licitaciones y contrataciones públicas (Compras MX) |
| `/empleo <puesto\|skill>` | `mx-job-search` | Vacantes de empleo en México/LATAM (tecnología) |
| `/universidades <carrera\|universidad>` | `mx-university-search` | Universidades de México y sus carreras |
| `/autos <marca> [modelo] [en <estado>]` | `mx-used-car-search` | Autos usados/seminuevos con índice de confianza (dealer, km/año, precio) |
| `/menu` | — | Muestra los botones de comandos |
| `/sat` | — | Submenú de consultas públicas del SAT (CFDI, 69-B, constancia, catálogos) |
| `/cancel` | — | Cancela un comando pendiente de completar |
| `/ask <mensaje>` | — | Enruta con IA a la skill correcta |
| `/help` | — | Lista los comandos |

## Modo interactivo

- **Menú de botones**: con `/menu` (o `/start`) el bot muestra un teclado con los comandos; tocar un botón ejecuta el comando sin escribir nada.
- **Submenú SAT**: con `/sat` (o el botón 🧾 /sat) se despliegan las consultas públicas del SAT: verificar un CFDI, listado 69-B, constancia por QR y catálogos. Usa la skill `sat-consulta` (dependencia `satcfdi`, instalada por `requirements.txt`).
- **Parámetros guiados**: si un comando necesita un dato y no lo recibes (p. ej. `/cp` sin código, `/precio` sin producto), el bot pregunta y tu siguiente mensaje completa el comando. Con `/cancel` se aborta la pregunta.
- **Ubicación 📍**: cuando un comando de lugar (`/clima`, `/ecobici`, `/gasolina`, `/aire`, `/banos`, `/ruta`) está esperando un dato, puedes responder enviando tu ubicación (📎 → Ubicación) y se usará como parámetro automáticamente.

## Ubicación compartida (GPS 📍)

En Telegram, pulsa **📎 → Ubicación** y envíala al bot. Se guarda como un **recurso compartido** para todas las skills de cercanía, por lo que luego puedes usar `/gasolina`, `/ecobici`, `/clima`, `/aire`, `/banos` o `/ruta a <destino>` **sin escribir el lugar**.

- **Privacidad**: las coordenadas se redondean (por defecto ±1.1 km, `BOT_BLUR_PRECISION=2`). No se usa tu ubicación exacta.
- La ubicación caduca (por defecto 1 hora, `BOT_LOCATION_MAX_AGE`).
- Si escribes un lugar en el comando, ese gana; si no, se usa la ubicación guardada; si tampoco hay, se usa `BOT_DEFAULT_PLACE`.
- Las skills de cercanía disponibles sin escribir el lugar son `/clima`, `/ecobici`, `/gasolina`, `/aire` y `/banos`.
- Opcional: persiste entre reinicios con `BOT_PERSISTENCE_FILE=.data/bot_data.pickle`.

## Logging

El bot registra en stdout (y opcionalmente en archivo) lo que hace: inicio y
comandos registrados, cada comando recibido (usuario, skill, args), la ejecución
de cada skill (tiempo y resultado) y los errores con contexto.

- `BOT_LOG_LEVEL`: `DEBUG`, `INFO` (por defecto), `WARNING` o `ERROR`.
- `BOT_LOG_FILE`: archivo de log opcional (además de stdout). Vacío = solo stdout.
- Los errores de red de Telegram (`NetworkError`, `TimedOut`, `RetryAfter`) se
  registran como **WARNING** sin traceback, porque la librería los reintenta sola.
- Los loggers ruidosos (`httpx`, `httpcore`, `telegram`) se fijan a `WARNING`.

```bash
BOT_LOG_LEVEL=DEBUG
BOT_LOG_FILE=.data/bot.log
```

Ejemplos de líneas:

```
2026-09-23 20:24:24 INFO  mx-bot: cmd=/clima user=123 skill=mx-weather args=[Guadalajara]
2026-09-23 20:24:25 INFO  mx-bot.runner: skill=mx-weather ok en 820 ms (rc=0)
2026-09-23 20:24:25 INFO  mx-bot: cmd=/clima respondido en 900 ms (312 chars)
2026-09-23 20:25:02 WARNING mx-bot: Telegram transitorio (se reintenta solo): NetworkError: ...
```

## Capa de IA opcional (`/ask`)

Sin configuración, `/ask` explica que requiere clave. Para activarla, en `.env`:

```bash
AI_API_KEY=sk-...                  # OpenAI, o vacío para Ollama local
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

Ollama local: `AI_API_KEY=ollama`, `AI_BASE_URL=http://localhost:11434/v1`, `AI_MODEL=llama3`. El modelo recibe el catálogo de skills y devuelve `{"skill": "...", "args": [...]}`; el bot ejecuta esa skill.

## Configuración extra

- `BOT_DEFAULT_PLACE`: ubicación por defecto para `/ecobici`, `/gasolina`, `/aire`, `/banos` (y `/clima`).
- `BOT_DEFAULT_LAT` / `BOT_DEFAULT_LON`: coordenadas por defecto opcionales.
- `BOT_ALLOWED_USER_IDS`: whitelist de IDs de Telegram (vacío = público).

## Despliegue con Docker

El bot ejecuta helpers de skills que viven en la **raíz del repo**, así que el
**build context debe ser la raíz** (no `tools/mx-telegram-bot`).

```bash
# Desde la raíz del repo
docker build -f tools/mx-telegram-bot/Dockerfile -t mx-telegram-bot .

# Ejecutar (el token se pasa por env-file o -e; nunca se hornea en la imagen)
docker run -d --name mx-telegram-bot \
  --restart unless-stopped \
  --env-file tools/mx-telegram-bot/.env \
  mx-telegram-bot

docker logs -f mx-telegram-bot
```

Con Docker Compose (desde `tools/mx-telegram-bot`):

```bash
docker compose up -d --build
docker compose logs -f
docker compose down
```

Notas:

- Es **long polling**: no expone puertos ni necesita webhook/túnel.
- No se hornea `.env` en la imagen (`.dockerignore` lo excluye); usa `--env-file` o variables de entorno.
- La imagen corre como usuario **no root** (`bot`, uid 10001).
- Para persistir la ubicación entre reinicios: define
  `BOT_PERSISTENCE_FILE=.data/bot_data.pickle` y monta un volumen en
  `/app/tools/mx-telegram-bot/.data` (el `docker-compose.yml` ya lo hace).
- Variables útiles: `BOT_LOG_LEVEL`, `BOT_ALLOWED_USER_IDS`, `BOT_DEFAULT_PLACE`.

## Arquitectura

```
tools/mx-telegram-bot/
├── bot/
│   ├── main.py          # construcción de la app, /start /help /ask /menu /sat, dispatch, 📍 ubicación
│   ├── config.py        # configuración desde .env
│   ├── runner.py        # ejecuta los helpers como subproceso y parsea JSON
│   ├── formatting.py    # utilidades de formato para Telegram (HTML)
│   ├── geo.py           # recurso compartido de ubicación (aprox. y por usuario)
│   ├── interactive.py   # menú de botones y completado guiado de parámetros
│   ├── ai.py            # enrutador opcional con LLM (OpenAI-compatible)
│   ├── logging_setup.py # configuración de logging (stdout/archivo, niveles)
│   ├── errors.py        # clasificación de errores de Telegram (transitorios)
│   └── skills/          # un módulo por skill
│       ├── registry.py  # registro central (SkillEntry)
│       └── <skill>.py   # handler + registro
├── run.py               # arranque rápido: venv + deps + .env + bot (--smoke/--check)
├── run.bat / run.sh     # wrappers de conveniencia para Windows y macOS/Linux
├── smoke_test.py        # prueba los handlers sin Telegram (incluye ubicación)
├── Dockerfile           # imagen de producción (build context = raíz del repo)
├── docker-compose.yml   # despliegue con Docker Compose
├── requirements.txt
└── .env.example
```

### Cómo añadir una skill

1. Añade la ruta del helper en `bot/runner.py` → `SKILL_SCRIPTS`.
2. Crea `bot/skills/<tu_skill>.py` (mira `weather.py` como plantilla):

```python
from .. import runner, formatting
from .registry import SkillEntry, register

async def mi_skill(update, context) -> str:
    data = await runner.run_skill("mi-skill-mx", ["--arg", "valor"])
    return formatting.section("Título", "...")

register(SkillEntry(command="miskill", description="...", usage="/miskill <x>", handler=mi_skill, skill_id="mi-skill-mx"))
```

3. Importa el módulo en `bot/skills/__init__.py`.

El registro central agrega el `CommandHandler` automáticamente; no hace falta tocar `main.py`.

## Probar sin Telegram

```bash
python run.py --smoke   # setup + smoke test
# o directamente, con el venv ya listo:
python smoke_test.py
```

Ejecuta cada handler con un `context` simulado y muestra la respuesta formateada.
