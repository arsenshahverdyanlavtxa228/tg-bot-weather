from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.database import Repository
from bot.handlers.common import is_cancel, render_weather
from bot.handlers.menu import show_main_menu
from bot.keyboards import cancel_kb, geo_results_kb
from bot.services import WeatherClient, WeatherError
from bot.services.i18n import Translator
from bot.states import FindCity

router = Router(name="find")

GEO_LIMIT = 5


@router.callback_query(F.data == "m:find")
async def start_find(cq: CallbackQuery, state: FSMContext, t: Translator) -> None:
    await state.set_state(FindCity.query)
    if isinstance(cq.message, Message):
        await cq.message.answer(t("find-prompt"), reply_markup=cancel_kb(t))
    await cq.answer()


@router.message(FindCity.query, F.text)
async def got_query(
    message: Message,
    state: FSMContext,
    t: Translator,
    weather: WeatherClient,
    repo: Repository,
    bot_username: str | None,
) -> None:
    if is_cancel(message.text, t):
        await state.clear()
        await message.answer(t("cancel"), reply_markup=ReplyKeyboardRemove())
        await show_main_menu(message, t, bot_username)
        return
    query = (message.text or "").strip()
    try:
        results = await weather.geocode(query, limit=GEO_LIMIT)
    except WeatherError:
        await message.answer(t("find-error"), reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    if not results:
        await message.answer(t("find-empty", query=query), reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    if len(results) == 1:
        loc = results[0]
        await message.answer(".", reply_markup=ReplyKeyboardRemove())
        placeholder = await message.answer("…")
        await state.clear()
        await render_weather(
            placeholder,
            repo=repo,
            weather=weather,
            t=t,
            lat=loc.lat,
            lon=loc.lon,
            display_name=loc.name,
        )
        return

    await state.update_data(
        results=[
            {
                "name": loc.name,
                "country": loc.country,
                "state": loc.state,
                "lat": loc.lat,
                "lon": loc.lon,
            }
            for loc in results
        ]
    )
    await message.answer(t("find-results"), reply_markup=ReplyKeyboardRemove())
    await message.answer(
        ".",
        reply_markup=geo_results_kb(results),
    )


@router.callback_query(FindCity.query, F.data.startswith("geo:"))
async def pick_result(
    cq: CallbackQuery,
    state: FSMContext,
    t: Translator,
    repo: Repository,
    weather: WeatherClient,
) -> None:
    idx = int((cq.data or "").split(":")[-1])
    data = await state.get_data()
    results = data.get("results") or []
    if idx >= len(results):
        await cq.answer()
        return
    picked = results[idx]
    await state.clear()
    if not isinstance(cq.message, Message):
        await cq.answer()
        return
    await render_weather(
        cq.message,
        repo=repo,
        weather=weather,
        t=t,
        lat=float(picked["lat"]),
        lon=float(picked["lon"]),
        display_name=str(picked["name"]),
    )
    await cq.answer()


@router.callback_query(F.data.startswith("w:refresh:"))
async def refresh_card(
    cq: CallbackQuery, t: Translator, repo: Repository, weather: WeatherClient
) -> None:
    _, _, lat_s, lon_s = (cq.data or "").split(":")
    lat, lon = float(lat_s), float(lon_s)
    if isinstance(cq.message, Message):
        await render_weather(cq.message, repo=repo, weather=weather, t=t, lat=lat, lon=lon)
    await cq.answer()


@router.callback_query(F.data.startswith("w:forecast:"))
async def show_forecast(
    cq: CallbackQuery, t: Translator, repo: Repository, weather: WeatherClient
) -> None:
    _, _, lat_s, lon_s = (cq.data or "").split(":")
    lat, lon = float(lat_s), float(lon_s)
    if isinstance(cq.message, Message):
        await render_weather(
            cq.message, repo=repo, weather=weather, t=t, lat=lat, lon=lon, with_forecast=True
        )
    await cq.answer()
