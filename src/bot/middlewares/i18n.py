from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.database.models import User
from bot.services.i18n import I18n


class I18nMiddleware(BaseMiddleware):
    def __init__(self, i18n: I18n) -> None:
        self._i18n = i18n

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        db_user: User | None = data.get("db_user")
        if db_user and db_user.locale in self._i18n.available:
            data["t"] = self._i18n.get(db_user.locale)
        else:
            tg_user = data.get("event_from_user")
            locale = None
            if tg_user and tg_user.language_code:
                lc = tg_user.language_code.split("-")[0]
                if lc in self._i18n.available:
                    locale = lc
            data["t"] = self._i18n.get(locale)
        return await handler(event, data)
