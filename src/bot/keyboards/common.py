from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.database.models import Favorite
from bot.services.formatters import country_flag
from bot.services.i18n import Translator
from bot.services.weather import GeoLocation


def main_menu_kb(t: Translator) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("menu-find"), callback_data="m:find")
    b.button(text=t("menu-favorites"), callback_data="m:favs")
    b.button(text=t("menu-settings"), callback_data="m:settings")
    b.adjust(2, 1)
    return b.as_markup()


def back_to_menu_kb(t: Translator) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t("back"), callback_data="m:main")]]
    )


def geo_results_kb(locations: Sequence[GeoLocation]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i, loc in enumerate(locations):
        flag = country_flag(loc.country)
        suffix = f", {loc.state}" if loc.state else ""
        country_part = f" ({loc.country})" if loc.country else ""
        b.button(
            text=f"{flag} {loc.name}{suffix}{country_part}".strip(),
            callback_data=f"geo:{i}",
        )
    b.button(text="⬅️", callback_data="m:main")
    b.adjust(1)
    return b.as_markup()


def weather_card_kb(
    t: Translator,
    *,
    lat: float,
    lon: float,
    is_favorite: bool,
    show_forecast_button: bool,
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("btn-refresh"), callback_data=f"w:refresh:{lat:.4f}:{lon:.4f}")
    if show_forecast_button:
        b.button(text=t("btn-forecast"), callback_data=f"w:forecast:{lat:.4f}:{lon:.4f}")
    if is_favorite:
        b.button(text=t("btn-favorite-remove"), callback_data=f"fav:rm:{lat:.4f}:{lon:.4f}")
    else:
        b.button(text=t("btn-favorite-add"), callback_data=f"fav:add:{lat:.4f}:{lon:.4f}")
    b.button(text=t("back"), callback_data="m:main")
    b.adjust(2, 1, 1)
    return b.as_markup()


def favorites_admin_kb(t: Translator, favs: Sequence[Favorite]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for fav in favs:
        flag = country_flag(fav.country_code)
        b.button(
            text=f"{flag} {fav.name}".strip(),
            callback_data=f"fav:view:{fav.id}",
        )
        b.button(text="🗑", callback_data=f"fav:del:{fav.id}")
    b.button(text=t("back"), callback_data="m:main")
    sizes = [2] * len(favs) + [1]
    b.adjust(*sizes)
    return b.as_markup()


def settings_kb(t: Translator) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("settings-language"), callback_data="s:lang")
    b.button(text=t("settings-units"), callback_data="s:units")
    b.button(text=t("back"), callback_data="m:main")
    b.adjust(2, 1)
    return b.as_markup()


def language_kb(t: Translator, current: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(
        text=("• " if current == "ru" else "") + t("language-ru"),
        callback_data="s:lang:ru",
    )
    b.button(
        text=("• " if current == "en" else "") + t("language-en"),
        callback_data="s:lang:en",
    )
    b.button(text=t("back"), callback_data="m:settings")
    b.adjust(2, 1)
    return b.as_markup()


def units_kb(t: Translator, current: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(
        text=("• " if current == "metric" else "") + t("units-metric"),
        callback_data="s:units:metric",
    )
    b.button(
        text=("• " if current == "imperial" else "") + t("units-imperial"),
        callback_data="s:units:imperial",
    )
    b.button(text=t("back"), callback_data="m:settings")
    b.adjust(1, 1, 1)
    return b.as_markup()


def cancel_kb(t: Translator) -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text=t("cancel"))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)
