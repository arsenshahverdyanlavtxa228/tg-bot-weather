from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import main_menu_kb
from bot.services.i18n import Translator

router = Router(name="menu")


async def show_main_menu(
    message: Message, t: Translator, bot_username: str | None, *, as_edit: bool = False
) -> None:
    text = t("start-welcome", botname=bot_username) if bot_username else t("start-welcome-no-name")
    kb = main_menu_kb(t)
    if as_edit:
        await message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, t: Translator, bot_username: str | None
) -> None:
    await state.clear()
    await show_main_menu(message, t, bot_username)


@router.callback_query(F.data == "m:main")
async def back_main(
    cq: CallbackQuery, state: FSMContext, t: Translator, bot_username: str | None
) -> None:
    await state.clear()
    if isinstance(cq.message, Message):
        await show_main_menu(cq.message, t, bot_username, as_edit=True)
    await cq.answer()
