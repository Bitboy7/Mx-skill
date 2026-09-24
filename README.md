# MX-skill 🇲🇽

![mx-skill thumbnail](docs/assets/mx-skill-thumbnail.jpg)

**Skills mexicanas para tu agente de IA**, más un **bot de Telegram** que las
expone como comandos. Es una adaptación al público mexicano de las skills de
[`NomaDamas/k-skill`](https://github.com/NomaDamas/k-skill), con fuentes
oficiales/públicas de México y sin API key.

- 20 skills MX (clima, aire, noticias, Lotería, CP, RFC, gasolina, trámites,
  transporte, comercio, gobierno…) en español.
- Bot de Telegram listo para usar (`/clima`, `/melate`, `/gasolina`, `/rfc`…).
- Compatibles con Claude Code, Codex, OpenCode, OpenClaw/ClawHub y otros agentes.
- Índice rápido de las skills MX: [`Skills/README.md`](Skills/README.md).

## Inicio rápido

### 1) Usar las skills con tu agente

```bash
# Instalar todas las skills MX
npx --yes skills add Bitboy7/Mx-skill --all -g

# Instalar una skill específica
npx --yes skills add Bitboy7/Mx-skill --skill mx-weather -g
```

Solo necesitas Node.js 18+ y `npx`. Detalles en [Instalación](docs/install.md).

### 2) Usar el bot de Telegram

```bash
cd tools/mx-telegram-bot
python run.py
```

`run.py` crea el venv, instala dependencias, crea `.env` y arranca el bot.
Necesitas un token de [@BotFather](https://t.me/BotFather) (`TELEGRAM_BOT_TOKEN`).
Detalles en [`tools/mx-telegram-bot/README.md`](tools/mx-telegram-bot/README.md).

## Skills MX (índice)

Todas usan fuentes públicas de México y **no requieren login ni API key**. La
columna "Comando" es el comando del bot de Telegram.

| Comando | Skill | Qué hace | Fuente |
| --- | --- | --- | --- |
| `/clima <ciudad>` | [`mx-weather`](mx-weather/) | Clima actual y pronóstico | Open-Meteo (ref. CONAGUA/SMN) |
| `/aire <ciudad>` | [`mx-air-quality`](mx-air-quality/) | Calidad del aire (PM2.5, PM10, US AQI) | Open-Meteo Air Quality (ref. SEDEMA/SEMARNAT) |
| `/noticias [query]` | [`mx-news`](mx-news/) | Portada o búsqueda de noticias | RSS de Google News (es-MX) |
| `/melate [números]` | [`melate-results`](melate-results/) | Resultados de la Lotería Nacional / verificar números | loterianacional.gob.mx |
| `/cp <cp>` | [`mx-zipcode-search`](mx-zipcode-search/) | Colonias/estado de un código postal | SEPOMEX (fuentes públicas) |
| `/rfc <rfc>` | [`sat-rfc-lookup`](sat-rfc-lookup/) | Valida la estructura de un RFC | SAT |
| `/ecobici <lugar>` | [`ecobici-cdmx`](ecobici-cdmx/) | Estaciones de Ecobici CDMX | GBFS oficial |
| `/cine [funciones]` | [`cine-mx`](cine-mx/) | Cartelera y funciones | Cinemex / Cinépolis |
| `/candidatos <nombre>` | [`comision-ine`](comision-ine/) | Candidaturas del INE | "Conóceles" |
| `/canasta [estado]` | [`precios-canasta`](precios-canasta/) | Precios de la canasta básica | PROFECO |
| `/ruta <origen> a <destino>` | [`mx-transit-route`](mx-transit-route/) | Ruta auto/caminando/bici | OSRM + Open-Meteo |
| `/gasolina <lugar>` | [`gas-prices-mx`](gas-prices-mx/) | Gasolineras más baratas | CRE (datos.gob.mx) |
| `/precio <producto>` | [`mercado-libre-search`](mercado-libre-search/) | Búsqueda de productos | API pública MLM |
| `/inmuebles [renta\|venta] <q>` | [`mx-real-estate`](mx-real-estate/) | Inmuebles en México | Mercado Libre Inmuebles |
| `/envio <guía>` | [`delivery-tracking-mx`](delivery-tracking-mx/) | Seguimiento de paquete | Estafeta |
| `/futbol [equipo\|jornada]` | [`mx-sports-results`](mx-sports-results/) | Liga MX / Liga de Expansión | API pública de ESPN |
| `/feriado [año\|proximos]` | [`mx-holiday-calendar`](mx-holiday-calendar/) | Días feriados oficiales | Nager.Date |
| `/banos <lugar>` | [`mx-restroom-nearby`](mx-restroom-nearby/) | Baños públicos cerca | OpenStreetMap / Overpass |
| `/licitaciones <palabra>` | [`compranet-search`](compranet-search/) | Licitaciones y contrataciones públicas | Compras MX vía LicitIA |
| `/bienestar [tema\|todos]` | [`beneficios-programas`](beneficios-programas/) | Programas para el Bienestar | Portal oficial |

Guías por skill: [`Skills/README.md`](Skills/README.md).

## Bot de Telegram

El bot funciona **sin IA** (comandos deterministas) y además es **interactivo**:

- Menú de botones con `/menu` o `/start`.
- Parámetros guiados: si falta un dato, el bot lo pregunta (`/cancel` para abortar).
- **Ubicación compartida 📍**: envía tu ubicación y úsala en `/clima`, `/ecobici`,
  `/gasolina`, `/aire`, `/banos` y `/ruta a <destino>` sin escribir el lugar.
- Capa de IA **opcional** (`/ask`) para enrutar un mensaje libre a la skill correcta.

| Comando | Skill | Qué hace |
| --- | --- | --- |
| `/clima <ciudad>` | `mx-weather` | Clima actual y pronóstico |
| `/aire <ciudad>` | `mx-air-quality` | Calidad del aire (PM2.5, PM10, US AQI) |
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
| `/futbol [equipo\|jornada\|expansion]` | `mx-sports-results` | Liga MX: tabla, equipo o jornada |
| `/feriado [año\|proximos]` | `mx-holiday-calendar` | Días feriados oficiales de México |
| `/banos <lugar>` | `mx-restroom-nearby` | Baños públicos cerca (OpenStreetMap) |
| `/licitaciones <palabra>` | `compranet-search` | Licitaciones y contrataciones públicas |
| `/bienestar [tema\|todos]` | `beneficios-programas` | Programas para el Bienestar |
| `/menu`, `/help`, `/cancel`, `/ask <mensaje>` | — | Menú, ayuda, cancelar y enrutado con IA |

## Estructura del repositorio

```
.
├── Skills/                 # Índice de las skills MX del bot
├── <skill-mx>/             # Cada skill MX (skill.json + instruction.md + scripts/ + tests/)
├── tools/mx-telegram-bot/  # Bot de Telegram (run.py, handlers, tests)
├── docs/                   # Guías de instalación, features y flujo del fork
└── packages/               # Paquetes npm del upstream (CLI, proxy, etc.)
```

Las skills viven en la **raíz** (layout plano que exige el CLI/plugin); `Skills/`
es solo un índice para ubicarlas rápido.

## Documentación

| Documento | Descripción |
| --- | --- |
| [Instalación](docs/install.md) | Instalación de skills, selectiva y pruebas locales |
| [Bot de Telegram](tools/mx-telegram-bot/README.md) | Comandos, configuración y arranque rápido |
| [Índice de skills MX](Skills/README.md) | Comandos, fuentes y guías |
| [Flujo del fork MX](docs/mx-fork-workflow.md) | Modelo de ramas y cómo traer skills del upstream |
| [Configuración común](docs/setup.md) | Credenciales y variables de entorno |
| [Seguridad/secretos](docs/security-and-secrets.md) | Manejo de credenciales y secretos |
| [Fuentes de referencia](docs/sources.md) | Librerías y documentos oficiales |

## Apoya el proyecto

Si te sirve, dale una estrella (los agentes no deben hacerlo solos):

```bash
gh repo star Bitboy7/Mx-skill
```

## Licencia

MIT (ver [LICENSE](LICENSE)). Los directorios del servidor proxy del upstream
tienen licencia AGPL-3.0-only:

- `packages/k-skill-proxy/` — AGPL-3.0-only
- `infra/k-skill-proxy-dashboard/` — AGPL-3.0-only
