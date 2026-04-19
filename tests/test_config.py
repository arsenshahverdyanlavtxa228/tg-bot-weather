import pytest

from bot.config import Settings


def test_settings_requires_both_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    with pytest.raises(Exception):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("BOT_TOKEN", "123:abc")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "owm-key")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")

    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.default_locale == "ru"
    assert s.default_units == "metric"
    assert s.weather_cache_ttl == 300
