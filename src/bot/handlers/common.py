from aiogram.enums import ParseMode
from aiogram.types import Message

from bot.database import Repository
from bot.keyboards import weather_card_kb
from bot.services import WeatherClient, WeatherError
from bot.services.formatters import format_weather_card
from bot.services.i18n import Translator

_CANCEL_TEXTS = frozenset({"✖️ Отмена", "✖️ Cancel"})


def is_cancel(text: str | None, t: Translator) -> bool:
    if not text:
        return False
    stripped = text.strip()
    return stripped == t("cancel") or stripped in _CANCEL_TEXTS


async def is_favorite(repo: Repository, lat: float, lon: float) -> bool:
    favs = await repo.list_favorites()
    return any(abs(f.lat - lat) < 1e-4 and abs(f.lon - lon) < 1e-4 for f in favs)


async def render_weather(
    message: Message,
    *,
    repo: Repository,
    weather: WeatherClient,
    t: Translator,
    lat: float,
    lon: float,
    display_name: str | None = None,
    with_forecast: bool = False,
    as_edit: bool = True,
) -> None:
    try:
        current = await weather.current(
            lat=lat, lon=lon, lang=repo.user.locale, units=repo.user.units
        )
        forecast = None
        if with_forecast:
            forecast = await weather.forecast_daily(
                lat=lat, lon=lon, lang=repo.user.locale, units=repo.user.units
            )
    except WeatherError:
        if as_edit:
            await message.edit_text(t("find-error"))
        else:
            await message.answer(t("find-error"))
        return

    text = format_weather_card(
        t, current, repo.user.units, forecast=forecast, display_name=display_name
    )
    fav = await is_favorite(repo, lat, lon)
    kb = weather_card_kb(
        t, lat=lat, lon=lon, is_favorite=fav, show_forecast_button=forecast is None
    )
    if as_edit:
        await message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
