from datetime import datetime

from bot.services.formatters import country_flag, format_weather_card, weather_emoji
from bot.services.i18n import I18n
from bot.services.weather import CurrentWeather, DailyForecast


def test_weather_emoji_known_and_unknown() -> None:
    assert weather_emoji("01d") == "☀️"
    assert weather_emoji("11n") == "⛈"
    assert weather_emoji("zzz") == "🌡"


def test_country_flag() -> None:
    assert country_flag("GB") == "🇬🇧"
    assert country_flag("us") == "🇺🇸"
    assert country_flag("") == ""
    assert country_flag("ZZZ") == ""
    assert country_flag(None) == ""


def test_format_weather_card_contains_key_fields(i18n: I18n) -> None:
    t = i18n.get("en")
    current = CurrentWeather(
        name="London",
        country="GB",
        temp=21.4,
        feels_like=20.1,
        description="clear sky",
        icon="01d",
        humidity=55,
        wind_speed=3.2,
        pressure=1015,
        observed_at=datetime(2026, 4, 1, 12, 34),
    )
    forecast = [
        DailyForecast(
            day=datetime(2026, 4, 2).date(), tmin=10, tmax=15, description="clouds", icon="03d"
        ),
    ]
    text = format_weather_card(t, current, "metric", forecast=forecast)
    assert "London" in text
    assert "🇬🇧" in text
    assert "21°C" in text
    assert "Humidity" in text
    assert "5-day forecast" in text
    assert "12:34" in text
