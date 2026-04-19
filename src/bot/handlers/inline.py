import hashlib
from typing import Any

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from bot.database import Repository
from bot.services import WeatherClient, WeatherError
from bot.services.formatters import format_inline
from bot.services.i18n import Translator

router = Router(name="inline")

MAX_RESULTS = 5


@router.inline_query()
async def inline_weather(
    query: InlineQuery, weather: WeatherClient, repo: Repository, t: Translator
) -> None:
    text = (query.query or "").strip()
    if not text:
        stub = InlineQueryResultArticle(
            id="empty",
            title=t("inline-empty-title"),
            description=t("inline-empty-desc"),
            input_message_content=InputTextMessageContent(message_text=t("inline-empty-title")),
        )
        await query.answer([stub], cache_time=60, is_personal=False)
        return

    try:
        matches = await weather.geocode(text, limit=MAX_RESULTS)
    except WeatherError:
        await query.answer([], cache_time=5, is_personal=True)
        return

    results: list[Any] = []
    for loc in matches:
        try:
            current = await weather.current(
                lat=loc.lat, lon=loc.lon, lang=repo.user.locale, units=repo.user.units
            )
        except WeatherError:
            continue
        title, desc, message_text = format_inline(
            t, current, repo.user.units, display_name=loc.name
        )
        key = hashlib.sha1(
            f"{loc.lat}:{loc.lon}:{repo.user.locale}:{repo.user.units}".encode()
        ).hexdigest()[:32]
        results.append(
            InlineQueryResultArticle(
                id=key,
                title=title,
                description=desc,
                input_message_content=InputTextMessageContent(
                    message_text=message_text, parse_mode=ParseMode.HTML
                ),
            )
        )

    await query.answer(results, cache_time=60, is_personal=True)
