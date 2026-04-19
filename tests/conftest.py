from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio

from bot.database import Repository, create_engine_and_session, ensure_user, init_models
from bot.services.i18n import I18n


@pytest_asyncio.fixture
async def repo() -> AsyncIterator[Repository]:
    factory = create_engine_and_session("sqlite+aiosqlite:///:memory:")
    await init_models(factory.engine)
    async with factory.session() as session:
        user = await ensure_user(session, tg_user_id=1, default_locale="ru", default_units="metric")
        yield Repository(session, user)
    await factory.dispose()


@pytest.fixture(scope="session")
def i18n() -> I18n:
    locales = Path(__file__).resolve().parents[1] / "src" / "bot" / "locales"
    return I18n(locales, default_locale="ru")
