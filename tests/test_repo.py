import pytest

from bot.database import Repository


@pytest.mark.asyncio
async def test_user_bootstrapped(repo: Repository) -> None:
    assert repo.user.tg_user_id == 1
    assert repo.user.locale == "ru"
    assert repo.user.units == "metric"


@pytest.mark.asyncio
async def test_add_list_delete(repo: Repository) -> None:
    a = await repo.add_favorite(name="London", lat=51.5, lon=-0.12, country_code="GB")
    await repo.add_favorite(name="Tokyo", lat=35.68, lon=139.69, country_code="JP")
    favs = await repo.list_favorites()
    assert [f.name for f in favs] == ["London", "Tokyo"]

    await repo.delete_favorite(a.id)
    favs = await repo.list_favorites()
    assert [f.name for f in favs] == ["Tokyo"]


@pytest.mark.asyncio
async def test_add_favorite_is_idempotent(repo: Repository) -> None:
    first = await repo.add_favorite(name="London", lat=51.5, lon=-0.12)
    second = await repo.add_favorite(name="London UK", lat=51.5, lon=-0.12)
    assert first.id == second.id
    favs = await repo.list_favorites()
    assert len(favs) == 1


@pytest.mark.asyncio
async def test_update_user(repo: Repository) -> None:
    await repo.update_user(locale="en", units="imperial")
    assert repo.user.locale == "en"
    assert repo.user.units == "imperial"
