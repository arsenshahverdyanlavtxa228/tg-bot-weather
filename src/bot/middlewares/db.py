from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TgUser

from bot.database import Repository, SessionFactory, ensure_user


class DBUserMiddleware(BaseMiddleware):
    """Opens a db session, bootstraps the user, injects a user-scoped Repository."""

    def __init__(self, factory: SessionFactory, default_locale: str, default_units: str) -> None:
        self._factory = factory
        self._default_locale = default_locale
        self._default_units = default_units

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        async with self._factory.session() as session:
            db_user = await ensure_user(
                session, tg_user.id, self._default_locale, self._default_units
            )
            data["session"] = session
            data["db_user"] = db_user
            data["repo"] = Repository(session, db_user)
            return await handler(event, data)
