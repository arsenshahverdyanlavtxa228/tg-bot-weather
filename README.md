# tg-bot-weather

[![CI](https://github.com/arsenshahverdyanlavtxa228/tg-bot-weather/actions/workflows/ci.yml/badge.svg)](https://github.com/arsenshahverdyanlavtxa228/tg-bot-weather/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2ea44f)](https://github.com/aiogram/aiogram)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Docker](https://img.shields.io/badge/docker-ready-2496ed.svg?logo=docker&logoColor=white)](Dockerfile)

> Weather Telegram bot. Current conditions, 5-day forecast, favorites, **inline-mode** via the OpenWeather API.
> Type a city or, from any chat, `@yourbot London` — the card lands right there.

---

## ✨ Features

- 🌦 **Current weather** — temperature, "feels like", condition, humidity, wind, pressure, country flag, timestamp.
- 📅 **5-day forecast** bucketed from OpenWeather's 3-hour series into daily min/max.
- 🔍 **City lookup** via OpenWeather Geocoding — picker when several locations match (e.g. London, UK vs. London, Ontario).
- ⭐ **Per-user favorites** — add once, view anytime.
- ✈️ **Inline mode** — type `@yourbot city_name` in any chat and send a weather card without switching windows.
- 🌐 **Per-user language** (RU / EN) and **units** (metric / imperial).
- ⚡ **TTL cache** that coalesces concurrent requests — keeps you under OpenWeather's free-tier rate limit.
- 🐳 **Production Dockerfile** — multi-stage, non-root, small image.
- 🚀 **One-click deploy** recipes for Railway, Render, Fly.io.
- ✅ **Type-safe** — ruff + mypy `strict` + pytest matrix on Python 3.11 / 3.12 / 3.13.

## 📸 Preview

```
┌───────────────────────────────────┐
│ ☀️ London 🇬🇧                     │
│ Now: 21°C (feels like 20°C)       │
│ Clear sky                         │
│                                   │
│ 💧 Humidity: 55%                  │
│ 💨 Wind: 3.2 m/s                  │
│ 🔽 Pressure: 1015 hPa             │
│                                   │
│ 5-day forecast                    │
│ ☀️ Mon 21.04: 14°C … 22°C, clear  │
│ 🌦 Tue 22.04: 12°C … 18°C, rain   │
│ …                                 │
│                                   │
│ [ 🔄 Refresh ] [ 📅 Forecast ]    │
│ [ ⭐ Add to favorites ]            │
└───────────────────────────────────┘
```

---

## 🚀 Quick start

### 1. Get your two secrets

1. **Bot token** — [@BotFather](https://t.me/BotFather) → `/newbot` → save the token.
2. **OpenWeather key** — sign up at [openweathermap.org/api](https://openweathermap.org/api) (free tier is enough).
   Activation takes up to ~10 minutes after signup.

### 2. Enable inline mode in @BotFather

```
/setinline → pick your bot → type a placeholder like "city name"
```

Without this step, `@yourbot London` does nothing.

### 3. Pick a deploy target

| Target | Difficulty | Cost | Storage |
|---|---|---|---|
| [Docker (local / VPS)](#-docker-local-or-vps) | ⭐ | free | volume |
| [Railway](#-railway) | ⭐ | free trial → $5/mo | volume |
| [Render](#-render) | ⭐⭐ | free worker | 1 GB disk |
| [Fly.io](#-flyio) | ⭐⭐ | free small VM | volume |

---

### 🐳 Docker (local or VPS)

```bash
git clone https://github.com/arsenshahverdyanlavtxa228/tg-bot-weather.git
cd tg-bot-weather
cp .env.example .env       # fill BOT_TOKEN and OPENWEATHER_API_KEY
docker compose up -d --build
docker compose logs -f bot
```

### 🚂 Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template)

1. Fork this repo.
2. Railway → **New Project → Deploy from GitHub** → pick the fork.
3. **Variables** → add `BOT_TOKEN` and `OPENWEATHER_API_KEY`.
4. **Settings → Volumes** → mount at `/app/data` (1 GB).
5. Deploy.

### 🎨 Render

1. Fork this repo.
2. [render.com](https://render.com) → **New → Blueprint** → pick the fork.
3. Render reads `render.yaml` and prompts for `BOT_TOKEN` + `OPENWEATHER_API_KEY`.
4. **Apply**. Worker deploys with a 1 GB attached disk.

### 🎈 Fly.io

```bash
fly launch --copy-config --no-deploy
fly volumes create bot_data --size 1
fly secrets set BOT_TOKEN=xxxxxx OPENWEATHER_API_KEY=yyyyyy
fly deploy
```

---

## ⚙️ Configuration

All settings are environment variables. See [`.env.example`](.env.example).

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | ✅ | — | Token from [@BotFather](https://t.me/BotFather). |
| `OPENWEATHER_API_KEY` | ✅ | — | Key from [openweathermap.org](https://openweathermap.org/api). |
| `DATABASE_URL` | — | `sqlite+aiosqlite:///./data/bot.db` | Any SQLAlchemy async URL. |
| `DEFAULT_LOCALE` | — | `ru` | `ru` / `en`. Per-user override from settings. |
| `DEFAULT_UNITS` | — | `metric` | `metric` / `imperial`. Per-user override. |
| `LOG_LEVEL` | — | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR`. |
| `DROP_PENDING_UPDATES` | — | `false` | Drop stale updates on startup. |
| `WEATHER_CACHE_TTL` | — | `300` | Seconds to cache OpenWeather responses (0–3600). |

## 🎮 How to use

```
/start                               → main menu

🔍 Find city                          → type a name → pick the match → weather card
  ↳ 🔄 Refresh    — re-fetch
  ↳ 📅 Forecast   — add 5-day forecast to the card
  ↳ ⭐ Add / 🗑 Remove favorite

⭐ Favorites                         → list; tap to open card; 🗑 to remove
⚙️ Settings                          → language, units

Inline mode: @yourbot London         → pick a card and send it into any chat
```

---

## 🧑‍💻 Local development

```bash
make dev         # create .venv + install runtime & dev deps
cp .env.example .env
make run
```

```bash
make lint         # ruff check
make fmt          # ruff format + auto-fix
make typecheck    # mypy strict
make test         # pytest
make cov          # tests with HTML coverage
```

### Project layout

```
src/bot/
  __main__.py              entrypoint — wires bot, dispatcher, middlewares, weather client
  config.py                pydantic-settings (.env loader)
  handlers/
    menu.py                /start and main-menu navigation
    find.py                city lookup FSM + weather card actions (refresh/forecast)
    favorites.py           view / add / remove favorites
    settings.py            language and units
    inline.py              inline-mode weather results
    common.py              render_weather helper, cancel-button detection
  keyboards/common.py      inline keyboard builders
  middlewares/
    db.py                  session + ensure_user + Repository
    i18n.py                per-user translator
  database/
    models.py              User, Favorite
    repo.py                user-scoped data access
    session.py             async engine + session factory
  services/
    weather.py             OpenWeather client (geocoding, current, forecast)
    cache.py               TTL cache with request coalescing
    formatters.py          weather-card rendering + emoji/flag helpers
    i18n.py                Fluent-based translator
  locales/ru/main.ftl
  locales/en/main.ftl
  states/weather.py        FSM state groups
```

---

## 🌍 Adding a new language

1. Copy `src/bot/locales/en/main.ftl` into `src/bot/locales/<lang>/main.ftl`.
2. Translate values. Keep keys identical.
3. Extend the language keyboard in `keyboards/common.py`.
4. Restart the bot.

## 🗺️ Roadmap ideas

- Geolocation message support (`/send_location`).
- Weather alerts via scheduled reminders.
- Hourly forecast view.
- Air-quality index (OpenWeather AQ endpoint).
- Postgres recipe verified in CI.

## 🤝 Contributing

PRs and issues welcome. Before submitting:

1. `make lint fmt typecheck test` all green.
2. Update `CHANGELOG.md` under `[Unreleased]`.

## 📄 License

[MIT](LICENSE) — do whatever, just keep the notice.
