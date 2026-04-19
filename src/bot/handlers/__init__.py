from aiogram import Dispatcher

from bot.handlers import favorites, find, inline, menu, settings


def register_all(dp: Dispatcher) -> None:
    dp.include_router(menu.router)
    dp.include_router(find.router)
    dp.include_router(favorites.router)
    dp.include_router(settings.router)
    dp.include_router(inline.router)


__all__ = ["register_all"]
