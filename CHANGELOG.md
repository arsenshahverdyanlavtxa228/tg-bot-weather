# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-19

### Added
- Initial release.
- `/start` main menu: 🔍 Find city, ⭐ Favorites, ⚙️ Settings.
- City lookup via OpenWeather Geocoding API; picker shown when multiple matches.
- Weather card: temperature, "feels like", condition with emoji, humidity, wind, pressure, country flag, observation time.
- 5-day forecast bucketed from OpenWeather's 3-hour series into daily min/max.
- Per-user favorites with CRUD (unique per coordinate).
- Inline mode: `@yourbot London` — returns up to 5 weather cards you can send into any chat.
- Per-user language (RU / EN) and units (metric / imperial) via `/start → Settings`.
- In-memory TTL cache that coalesces concurrent identical requests — stays under the OpenWeather free-tier rate limit.
- Fluent-based i18n (RU + EN), locales auto-discovered.
- Multi-stage Dockerfile (non-root), docker-compose.
- Deploy recipes: Railway (`railway.json`), Render (`render.yaml`), Fly.io (`fly.toml`).
- CI: ruff lint + format check, mypy strict, pytest matrix on Python 3.11 / 3.12 / 3.13, Docker build.
- Release workflow pushes an image to GHCR on `v*.*.*` tags.

[Unreleased]: https://github.com/arsenshahverdyanlavtxa228/tg-bot-weather/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/arsenshahverdyanlavtxa228/tg-bot-weather/releases/tag/v0.1.0
