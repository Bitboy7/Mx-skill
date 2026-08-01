# MX Telegram Bot

Bot de Telegram en Python que expone las **skills MX** del repositorio `k-skill` como comandos. Cada comando ejecuta el helper de la skill correspondiente (subproceso) y formatea el JSON en una respuesta legible.

- ✅ Funciona **sin IA**: comandos deterministas que llaman a las skills.
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

## Ejecutar

```bash
python -m bot.main
```

## Comandos

| Comando | Skill interna | Qué hace |
| --- | --- | --- |
| `/clima <ciudad>` | `mx-weather` | Clima actual y pronóstico |
| `/noticias [query]` | `mx-news` | Portada o búsqueda de noticias |
| `/melate [números]` | `melate-results` | Resultados de la Lotería o verifica números |
| `/cp <cp>` | `mx-zipcode-search` | Colonias/estado de un código postal |
| `/rfc <rfc>` | `sat-rfc-lookup` | Valida la estructura de un RFC |
| `/ecobici <lugar>` | `ecobici-cdmx` | Ecobici CDMX con bicis disponibles |
| `/cine [funciones ...]` | `cine-mx` | Cartelera y funciones (Cinemex) |
| `/candidatos <nombre>` | `comision-ine` | Candidatas y candidatos del INE |
| `/canasta [estado]` | `precios-canasta` | Precios de la canasta básica |
| `/ruta <origen> a <destino>` | `mx-transit-route` | Ruta auto/caminando/bici |
| `/gasolina <lugar>` | `gas-prices-mx` | Gasolineras más baratas cerca |
| `/precio <producto>` | `mercado-libre-search` | Búsqueda en Mercado Libre |
| `/inmuebles [renta\|venta] <q>` | `mx-real-estate` | Inmuebles en México |
| `/envio <guía>` | `delivery-tracking-mx` | Seguimiento de paquete (Estafeta) |
| `/ask <mensaje>` | — | Enruta con IA a la skill correcta |
| `/help` | — | Lista los comandos |

## Ubicación compartida (GPS 📍)

En Telegram, pulsa **📎 → Ubicación** y envíala al bot. Se guarda como un **recurso compartido** para todas las skills de cercanía, por lo que luego puedes usar `/gasolina`, `/ecobici`, `/clima` o `/ruta a <destino>` **sin escribir el lugar**.

- **Privacidad**: las coordenadas se redondean (por defecto ±1.1 km, `BOT_BLUR_PRECISION=2`). No se usa tu ubicación exacta.
- La ubicación caduca (por defecto 1 hora, `BOT_LOCATION_MAX_AGE`).
- Si escribes un lugar en el comando, ese gana; si no, se usa la ubicación guardada; si tampoco hay, se usa `BOT_DEFAULT_PLACE`.
- Opcional: persiste entre reinicios con `BOT_PERSISTENCE_FILE=.data/bot_data.pickle`.

## Capa de IA opcional (`/ask`)

Sin configuración, `/ask` explica que requiere clave. Para activarla, en `.env`:

```bash
AI_API_KEY=sk-...                  # OpenAI, o vacío para Ollama local
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

Ollama local: `AI_API_KEY=ollama`, `AI_BASE_URL=http://localhost:11434/v1`, `AI_MODEL=llama3`. El modelo recibe el catálogo de skills y devuelve `{"skill": "...", "args": [...]}`; el bot ejecuta esa skill.

## Configuración extra

- `BOT_DEFAULT_PLACE`: ubicación por defecto para `/ecobici`, `/gasolina` (y `/clima`).
- `BOT_DEFAULT_LAT` / `BOT_DEFAULT_LON`: coordenadas por defecto opcionales.
- `BOT_ALLOWED_USER_IDS`: whitelist de IDs de Telegram (vacío = público).

## Arquitectura

```
tools/mx-telegram-bot/
├── bot/
│   ├── main.py          # construcción de la app, /start /help /ask, dispatch, 📍 ubicación
│   ├── config.py        # configuración desde .env
│   ├── runner.py        # ejecuta los helpers como subproceso y parsea JSON
│   ├── formatting.py    # utilidades de formato para Telegram (HTML)
│   ├── geo.py           # recurso compartido de ubicación (aprox. y por usuario)
│   ├── ai.py            # enrutador opcional con LLM (OpenAI-compatible)
│   └── skills/          # un módulo por skill
│       ├── registry.py  # registro central (SkillEntry)
│       └── <skill>.py   # handler + registro
├── smoke_test.py        # prueba los handlers sin Telegram (incluye ubicación)
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
python smoke_test.py
```

Ejecuta cada handler con un `context` simulado y muestra la respuesta formateada.
