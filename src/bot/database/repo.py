from collections.abc import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Favorite, User


class Repository:
    """User-scoped data access."""

    def __init__(self, session: AsyncSession, user: User) -> None:
        self.session = session
        self.user = user

    @property
    def user_id(self) -> int:
        return self.user.id

    async def update_user(self, **fields: object) -> User:
        for key, value in fields.items():
            setattr(self.user, key, value)
        await self.session.flush()
        return self.user

    # ---------- Favorites ----------

    async def list_favorites(self) -> Sequence[Favorite]:
        result = await self.session.execute(
            select(Favorite)
            .where(Favorite.user_id == self.user_id)
            .order_by(Favorite.position, Favorite.id)
        )
        return result.scalars().all()

    async def get_favorite(self, favorite_id: int) -> Favorite | None:
        result = await self.session.execute(
            select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == self.user_id)
        )
        return result.scalar_one_or_none()

    async def add_favorite(
        self,
        *,
        name: str,
        lat: float,
        lon: float,
        country_code: str | None = None,
        state: str | None = None,
    ) -> Favorite:
        existing = await self.session.execute(
            select(Favorite).where(
                Favorite.user_id == self.user_id,
                Favorite.lat == lat,
                Favorite.lon == lon,
            )
        )
        already = existing.scalar_one_or_none()
        if already is not None:
            return already

        max_pos = await self.session.execute(
            select(func.coalesce(func.max(Favorite.position), -1)).where(
                Favorite.user_id == self.user_id
            )
        )
        fav = Favorite(
            user_id=self.user_id,
            name=name,
            country_code=country_code,
            state=state,
            lat=lat,
            lon=lon,
            position=int(max_pos.scalar_one()) + 1,
        )
        self.session.add(fav)
        await self.session.flush()
        return fav

    async def delete_favorite(self, favorite_id: int) -> None:
        await self.session.execute(
            delete(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == self.user_id)
        )


async def ensure_user(
    session: AsyncSession, tg_user_id: int, default_locale: str, default_units: str
) -> User:
    result = await session.execute(select(User).where(User.tg_user_id == tg_user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(tg_user_id=tg_user_id, locale=default_locale, units=default_units)
        session.add(user)
        await session.flush()
    return user
