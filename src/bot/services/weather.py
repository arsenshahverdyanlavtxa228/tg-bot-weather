from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import aiohttp

from bot.services.cache import TTLCache

GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


class WeatherError(RuntimeError):
    """Raised when the upstream API returns a non-2xx response or malformed data."""


@dataclass(frozen=True, slots=True)
class GeoLocation:
    name: str
    country: str | None
    state: str | None
    lat: float
    lon: float


@dataclass(frozen=True, slots=True)
class CurrentWeather:
    name: str
    country: str | None
    temp: float
    feels_like: float
    description: str
    icon: str
    humidity: int
    wind_speed: float
    pressure: int
    observed_at: datetime


@dataclass(frozen=True, slots=True)
class DailyForecast:
    day: date
    tmin: float
    tmax: float
    description: str
    icon: str


class WeatherClient:
    """Thin async wrapper around the OpenWeather 2.5 API + geocoding."""

    def __init__(
        self,
        api_key: str,
        *,
        session: aiohttp.ClientSession | None = None,
        cache_ttl: float = 300.0,
        timeout: float = 10.0,
    ) -> None:
        self._api_key = api_key
        self._owned_session = session is None
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._cache = TTLCache(cache_ttl)

    async def __aenter__(self) -> "WeatherClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
            self._owned_session = True
        return self._session

    async def close(self) -> None:
        if self._owned_session and self._session is not None and not self._session.closed:
            await self._session.close()

    # ---------- Raw HTTP ----------

    async def _get(self, url: str, params: dict[str, Any]) -> Any:
        params = {**params, "appid": self._api_key}
        session = await self._ensure_session()
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise WeatherError(f"HTTP {resp.status}: {body[:200]}")
                return await resp.json()
        except aiohttp.ClientError as exc:
            raise WeatherError(str(exc)) from exc

    # ---------- Public API ----------

    async def geocode(self, query: str, *, limit: int = 5) -> list[GeoLocation]:
        key = f"geo:{query.lower()}:{limit}"

        async def load() -> list[GeoLocation]:
            data = await self._get(GEO_URL, {"q": query, "limit": limit})
            return [
                GeoLocation(
                    name=item.get("name", query),
                    country=item.get("country"),
                    state=item.get("state"),
                    lat=float(item["lat"]),
                    lon=float(item["lon"]),
                )
                for item in (data or [])
            ]

        return await self._cache.get_or_set(key, load)

    async def current(
        self, *, lat: float, lon: float, lang: str = "en", units: str = "metric"
    ) -> CurrentWeather:
        key = f"cur:{lat:.4f}:{lon:.4f}:{lang}:{units}"

        async def load() -> CurrentWeather:
            data = await self._get(
                CURRENT_URL, {"lat": lat, "lon": lon, "lang": lang, "units": units}
            )
            weather = (data.get("weather") or [{}])[0]
            main = data.get("main") or {}
            wind = data.get("wind") or {}
            sys = data.get("sys") or {}
            return CurrentWeather(
                name=str(data.get("name") or ""),
                country=sys.get("country"),
                temp=float(main.get("temp", 0.0)),
                feels_like=float(main.get("feels_like", 0.0)),
                description=str(weather.get("description", "")),
                icon=str(weather.get("icon", "")),
                humidity=int(main.get("humidity", 0)),
                wind_speed=float(wind.get("speed", 0.0)),
                pressure=int(main.get("pressure", 0)),
                observed_at=datetime.fromtimestamp(int(data.get("dt", 0))),
            )

        return await self._cache.get_or_set(key, load)

    async def forecast_daily(
        self, *, lat: float, lon: float, lang: str = "en", units: str = "metric"
    ) -> list[DailyForecast]:
        key = f"fc:{lat:.4f}:{lon:.4f}:{lang}:{units}"

        async def load() -> list[DailyForecast]:
            data = await self._get(
                FORECAST_URL, {"lat": lat, "lon": lon, "lang": lang, "units": units}
            )
            return _bucket_forecast(data)

        return await self._cache.get_or_set(key, load)


def _bucket_forecast(data: dict[str, Any]) -> list[DailyForecast]:
    """Turn the 3-hour forecast list into up to 5 daily min/max buckets."""
    by_day: dict[date, dict[str, Any]] = {}
    for item in data.get("list") or []:
        ts = datetime.fromtimestamp(int(item.get("dt", 0)))
        day = ts.date()
        main = item.get("main") or {}
        weather = (item.get("weather") or [{}])[0]
        tmin = float(main.get("temp_min", main.get("temp", 0.0)))
        tmax = float(main.get("temp_max", main.get("temp", 0.0)))

        bucket = by_day.setdefault(
            day,
            {
                "tmin": tmin,
                "tmax": tmax,
                "noon_dt": ts,
                "desc": weather.get("description", ""),
                "icon": weather.get("icon", ""),
            },
        )
        bucket["tmin"] = min(float(bucket["tmin"]), tmin)
        bucket["tmax"] = max(float(bucket["tmax"]), tmax)
        # Prefer the observation closest to noon for the daily label.
        cur_diff = abs(bucket["noon_dt"].hour - 12)
        new_diff = abs(ts.hour - 12)
        if new_diff < cur_diff:
            bucket["noon_dt"] = ts
            bucket["desc"] = weather.get("description", bucket["desc"])
            bucket["icon"] = weather.get("icon", bucket["icon"])

    days = sorted(by_day.keys())[:5]
    return [
        DailyForecast(
            day=d,
            tmin=float(by_day[d]["tmin"]),
            tmax=float(by_day[d]["tmax"]),
            description=str(by_day[d]["desc"]),
            icon=str(by_day[d]["icon"]),
        )
        for d in days
    ]
