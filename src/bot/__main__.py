import asyncio
import contextlib
import logging
from pathlib import Path

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_settings
from bot.database import create_engine_and_session, init_models
from bot.handlers import register_all
from bot.middlewares import DBUserMiddleware, I18nMiddleware
from bot.services import WeatherClient
from bot.services.i18n import I18n


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
    )


async def amain() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)
    log = structlog.get_logger("bot")

    session_factory = create_engine_and_session(settings.database_url)
    await init_models(session_factory.engine)

    locales_dir = Path(__file__).parent / "locales"
    i18n = I18n(locales_dir, default_locale=settings.default_locale)

    weather = WeatherClient(
        settings.openweather_api_key.get_secret_value(),
        cache_ttl=settings.weather_cache_ttl,
    )

    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    me = await bot.get_me()

    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(
        DBUserMiddleware(session_factory, settings.default_locale, settings.default_units)
    )
    dp.update.middleware(I18nMiddleware(i18n))
    dp["weather"] = weather
    dp["bot_username"] = me.username

    register_all(dp)

    log.info("bot.starting", username=me.username)
    try:
        await bot.delete_webhook(drop_pending_updates=settings.drop_pending_updates)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await weather.close()
        await bot.session.close()
        await session_factory.dispose()


def main() -> None:
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(amain())


if __name__ == "__main__":
    main()
