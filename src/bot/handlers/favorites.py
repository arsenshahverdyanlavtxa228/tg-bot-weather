from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message

from bot.database import Repository
from bot.handlers.common import render_weather
from bot.keyboards import back_to_menu_kb, favorites_admin_kb
from bot.services import WeatherClient
from bot.services.i18n import Translator

router = Router(name="favorites")


async def _list_favorites(message: Message, repo: Repository, t: Translator) -> None:
    favs = await repo.list_favorites()
    if not favs:
        await message.edit_text(
            t("favorites-empty"), reply_markup=back_to_menu_kb(t), parse_mode=ParseMode.HTML
        )
        return
    await message.edit_text(
        t("menu-favorites"),
        reply_markup=favorites_admin_kb(t, favs),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "m:favs")
async def open_favs(cq: CallbackQuery, repo: Repository, t: Translator) -> None:
    if isinstance(cq.message, Message):
        await _list_favorites(cq.message, repo, t)
    await cq.answer()


@router.callback_query(F.data.startswith("fav:view:"))
async def view_favorite(
    cq: CallbackQuery, repo: Repository, t: Translator, weather: WeatherClient
) -> None:
    fav_id = int((cq.data or "").split(":")[-1])
    fav = await repo.get_favorite(fav_id)
    if fav is None or not isinstance(cq.message, Message):
        await cq.answer()
        return
    await render_weather(
        cq.message,
        repo=repo,
        weather=weather,
        t=t,
        lat=fav.lat,
        lon=fav.lon,
        display_name=fav.name,
    )
    await cq.answer()


@router.callback_query(F.data.startswith("fav:del:"))
async def delete_favorite(cq: CallbackQuery, repo: Repository, t: Translator) -> None:
    fav_id = int((cq.data or "").split(":")[-1])
    await repo.delete_favorite(fav_id)
    if isinstance(cq.message, Message):
        await _list_favorites(cq.message, repo, t)
    await cq.answer(t("favorite-removed"))


@router.callback_query(F.data.startswith("fav:add:"))
async def add_favorite(
    cq: CallbackQuery, repo: Repository, t: Translator, weather: WeatherClient
) -> None:
    _, _, lat_s, lon_s = (cq.data or "").split(":")
    lat, lon = float(lat_s), float(lon_s)
    try:
        current = await weather.current(
            lat=lat, lon=lon, lang=repo.user.locale, units=repo.user.units
        )
        await repo.add_favorite(
            name=current.name or f"{lat:.2f},{lon:.2f}",
            lat=lat,
            lon=lon,
            country_code=current.country,
        )
    except Exception:
        await cq.answer(t("error-generic"))
        return
    if isinstance(cq.message, Message):
        await render_weather(cq.message, repo=repo, weather=weather, t=t, lat=lat, lon=lon)
    await cq.answer(t("favorite-added"))


@router.callback_query(F.data.startswith("fav:rm:"))
async def remove_favorite_from_card(
    cq: CallbackQuery, repo: Repository, t: Translator, weather: WeatherClient
) -> None:
    _, _, lat_s, lon_s = (cq.data or "").split(":")
    lat, lon = float(lat_s), float(lon_s)
    favs = await repo.list_favorites()
    for fav in favs:
        if abs(fav.lat - lat) < 1e-4 and abs(fav.lon - lon) < 1e-4:
            await repo.delete_favorite(fav.id)
            break
    if isinstance(cq.message, Message):
        await render_weather(cq.message, repo=repo, weather=weather, t=t, lat=lat, lon=lon)
    await cq.answer(t("favorite-removed"))
