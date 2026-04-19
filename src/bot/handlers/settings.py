from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message

from bot.database import Repository
from bot.keyboards import language_kb, settings_kb, units_kb
from bot.services.i18n import Translator

router = Router(name="settings")


def _title(t: Translator) -> str:
    return t("settings-title")


@router.callback_query(F.data == "m:settings")
async def open_settings(cq: CallbackQuery, t: Translator) -> None:
    if isinstance(cq.message, Message):
        await cq.message.edit_text(
            _title(t), reply_markup=settings_kb(t), parse_mode=ParseMode.HTML
        )
    await cq.answer()


@router.callback_query(F.data == "s:lang")
async def open_lang(cq: CallbackQuery, repo: Repository, t: Translator) -> None:
    if isinstance(cq.message, Message):
        await cq.message.edit_reply_markup(reply_markup=language_kb(t, repo.user.locale))
    await cq.answer()


@router.callback_query(F.data.in_({"s:lang:ru", "s:lang:en"}))
async def set_lang(cq: CallbackQuery, repo: Repository, t: Translator) -> None:
    locale = (cq.data or "").split(":")[-1]
    await repo.update_user(locale=locale)
    await cq.answer(t("language-set"))
    if isinstance(cq.message, Message):
        await cq.message.edit_text(
            _title(t), reply_markup=settings_kb(t), parse_mode=ParseMode.HTML
        )


@router.callback_query(F.data == "s:units")
async def open_units(cq: CallbackQuery, repo: Repository, t: Translator) -> None:
    if isinstance(cq.message, Message):
        await cq.message.edit_reply_markup(reply_markup=units_kb(t, repo.user.units))
    await cq.answer()


@router.callback_query(F.data.in_({"s:units:metric", "s:units:imperial"}))
async def set_units(cq: CallbackQuery, repo: Repository, t: Translator) -> None:
    units = (cq.data or "").split(":")[-1]
    await repo.update_user(units=units)
    await cq.answer(t("units-saved"))
    if isinstance(cq.message, Message):
        await cq.message.edit_text(
            _title(t), reply_markup=settings_kb(t), parse_mode=ParseMode.HTML
        )
