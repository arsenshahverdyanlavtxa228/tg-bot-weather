import re

import pytest
from aioresponses import aioresponses

from bot.services.weather import (
    CURRENT_URL,
    FORECAST_URL,
    GEO_URL,
    WeatherClient,
    WeatherError,
)


@pytest.mark.asyncio
async def test_geocode_parses_results() -> None:
    client = WeatherClient("dummy")
    with aioresponses() as mock:
        mock.get(
            re.compile(rf"^{re.escape(GEO_URL)}.*"),
            payload=[
                {"name": "London", "country": "GB", "state": "England", "lat": 51.5, "lon": -0.12},
                {
                    "name": "London",
                    "country": "CA",
                    "state": "Ontario",
                    "lat": 42.98,
                    "lon": -81.24,
                },
            ],
        )
        results = await client.geocode("London")
    assert len(results) == 2
    assert results[0].country == "GB"
    assert pytest.approx(results[0].lat, 1e-3) == 51.5
    await client.close()


@pytest.mark.asyncio
async def test_current_parses_payload() -> None:
    client = WeatherClient("dummy")
    payload = {
        "name": "London",
        "dt": 1_700_000_000,
        "weather": [{"description": "clear sky", "icon": "01d"}],
        "main": {"temp": 20.5, "feels_like": 20.0, "humidity": 55, "pressure": 1015},
        "wind": {"speed": 3.2},
        "sys": {"country": "GB"},
    }
    with aioresponses() as mock:
        mock.get(re.compile(rf"^{re.escape(CURRENT_URL)}.*"), payload=payload)
        current = await client.current(lat=51.5, lon=-0.12)
    assert current.name == "London"
    assert current.humidity == 55
    assert current.description == "clear sky"
    assert current.icon == "01d"
    await client.close()


@pytest.mark.asyncio
async def test_forecast_buckets_days() -> None:
    # Use timestamps that land squarely inside the same UTC day and the next.
    client = WeatherClient("dummy")
    # 2023-11-14 10:00 UTC and +3h, +21h (straddles into 2023-11-15 07:00 UTC).
    payload = {
        "list": [
            {
                "dt": 1_699_956_000,  # 2023-11-14 10:00 UTC
                "main": {"temp": 10, "temp_min": 9, "temp_max": 11},
                "weather": [{"description": "clouds", "icon": "03d"}],
            },
            {
                "dt": 1_699_966_800,  # 2023-11-14 13:00 UTC
                "main": {"temp": 12, "temp_min": 11, "temp_max": 14},
                "weather": [{"description": "clouds", "icon": "03d"}],
            },
            {
                "dt": 1_700_038_800,  # 2023-11-15 09:00 UTC (next day)
                "main": {"temp": 15, "temp_min": 13, "temp_max": 18},
                "weather": [{"description": "sunny", "icon": "01d"}],
            },
        ]
    }
    with aioresponses() as mock:
        mock.get(re.compile(rf"^{re.escape(FORECAST_URL)}.*"), payload=payload)
        days = await client.forecast_daily(lat=51.5, lon=-0.12)
    assert len(days) == 2
    # day 1 aggregates the first two items → tmin=9, tmax=14
    assert days[0].tmin == 9
    assert days[0].tmax == 14
    # day 2 has only the third item → tmin=13, tmax=18
    assert days[1].tmin == 13
    assert days[1].tmax == 18
    await client.close()


@pytest.mark.asyncio
async def test_error_on_bad_status() -> None:
    client = WeatherClient("dummy")
    with aioresponses() as mock:
        mock.get(re.compile(rf"^{re.escape(CURRENT_URL)}.*"), status=401, body="Unauthorized")
        with pytest.raises(WeatherError):
            await client.current(lat=1, lon=2)
    await client.close()
