from bot.services.i18n import Translator
from bot.services.weather import CurrentWeather, DailyForecast

# Condition code → emoji. See https://openweathermap.org/weather-conditions
_ICON_EMOJI: dict[str, str] = {
    "01d": "☀️",
    "01n": "🌙",
    "02d": "🌤",
    "02n": "☁️",
    "03d": "☁️",
    "03n": "☁️",
    "04d": "☁️",
    "04n": "☁️",
    "09d": "🌧",
    "09n": "🌧",
    "10d": "🌦",
    "10n": "🌧",
    "11d": "⛈",
    "11n": "⛈",
    "13d": "❄️",
    "13n": "❄️",
    "50d": "🌫",
    "50n": "🌫",
}


def weather_emoji(icon: str) -> str:
    return _ICON_EMOJI.get(icon, "🌡")


def country_flag(country_code: str | None) -> str:
    if not country_code or len(country_code) != 2 or not country_code.isalpha():
        return ""
    offset = 0x1F1E6
    base = ord("A")
    return "".join(chr(offset + ord(ch.upper()) - base) for ch in country_code)


def _temp(value: float, units: str) -> str:
    unit = "°C" if units == "metric" else "°F"
    return f"{round(value)}{unit}"


def _wind_unit(units: str) -> str:
    return "m/s" if units == "metric" else "mph"


def format_weather_card(
    t: Translator,
    current: CurrentWeather,
    units: str,
    *,
    forecast: list[DailyForecast] | None = None,
    display_name: str | None = None,
) -> str:
    flag = country_flag(current.country)
    flag_part = f" {flag}" if flag else ""
    name = display_name or current.name or ""

    lines = [
        t("card-header", emoji=weather_emoji(current.icon), name=name, flag=flag_part),
        t("card-now", temp=_temp(current.temp, units), feels=_temp(current.feels_like, units)),
        t("card-desc", desc=current.description.capitalize()),
        "",
        t(
            "card-details",
            humidity=current.humidity,
            wind=round(current.wind_speed, 1),
            wind_unit=_wind_unit(units),
            pressure=current.pressure,
        ),
    ]

    if forecast:
        lines.append("")
        lines.append(t("card-forecast-header"))
        for day in forecast:
            lines.append(
                t(
                    "card-forecast-line",
                    emoji=weather_emoji(day.icon),
                    date=day.day.strftime("%a %d.%m"),
                    tmin=_temp(day.tmin, units),
                    tmax=_temp(day.tmax, units),
                    desc=day.description.capitalize(),
                )
            )

    lines.append("")
    lines.append("<i>" + t("updated-at", time=current.observed_at.strftime("%H:%M")) + "</i>")
    return "\n".join(lines)


def format_inline(
    t: Translator, current: CurrentWeather, units: str, display_name: str | None = None
) -> tuple[str, str, str]:
    """Returns (title, description, message_text) for an inline result."""
    flag = country_flag(current.country)
    flag_part = f" {flag}" if flag else ""
    name = display_name or current.name or ""
    title = t(
        "inline-title",
        emoji=weather_emoji(current.icon),
        name=name,
        flag=flag_part,
        temp=_temp(current.temp, units),
    )
    desc = t(
        "inline-desc",
        desc=current.description.capitalize(),
        feels=_temp(current.feels_like, units),
        humidity=current.humidity,
    )
    message = format_weather_card(t, current, units, display_name=display_name)
    return title, desc, message
