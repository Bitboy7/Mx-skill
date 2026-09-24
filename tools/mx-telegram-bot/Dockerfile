# syntax=docker/dockerfile:1

# Bot de Telegram de skills MX.
#
# El bot ejecuta los helpers de las skills, que viven en la RAÍZ del repo
# (por ejemplo mx-weather/scripts/mx_weather.py), así que el build context debe
# ser la raíz del repositorio y la imagen conserva el layout del repo:
#
#   docker build -f tools/mx-telegram-bot/Dockerfile -t mx-telegram-bot .
#   docker run --rm --env-file tools/mx-telegram-bot/.env mx-telegram-bot
#
# Es long polling: no expone puertos ni necesita webhook/túnel.

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    BOT_LOG_LEVEL=INFO

WORKDIR /app

# 1) Dependencias del bot (capa cacheable).
COPY tools/mx-telegram-bot/requirements.txt ./tools/mx-telegram-bot/requirements.txt
RUN pip install --no-cache-dir -r tools/mx-telegram-bot/requirements.txt

# 2) Código del bot + skills MX (helpers en la raíz del repo).
#    .dockerignore excluye .env, .venv, node_modules, tests, etc.
COPY . .

# 3) Usuario sin privilegios y directorio de persistencia escribible.
RUN useradd --create-home --uid 10001 bot \
    && mkdir -p /app/tools/mx-telegram-bot/.data \
    && chown -R bot:bot /app
USER bot

WORKDIR /app/tools/mx-telegram-bot

CMD ["python", "-m", "bot.main"]
