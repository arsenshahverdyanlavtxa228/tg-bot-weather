import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar, cast

T = TypeVar("T")


class TTLCache:
    """Asyncio-friendly TTL cache. Coalesces concurrent requests for the same key.

    Not generic at the class level — callers get back the loader's return type,
    so one cache instance can hold heterogeneous values.
    """

    def __init__(self, ttl_seconds: float) -> None:
        self.ttl = ttl_seconds
        self._values: dict[str, tuple[float, object]] = {}
        self._pending: dict[str, asyncio.Future[object]] = {}

    def _fresh(self, expiry: float) -> bool:
        return expiry > time.monotonic()

    async def get_or_set(self, key: str, loader: Callable[[], Awaitable[T]]) -> T:
        cached = self._values.get(key)
        if cached is not None and self._fresh(cached[0]):
            return cast(T, cached[1])

        pending = self._pending.get(key)
        if pending is not None:
            return cast(T, await pending)

        loop = asyncio.get_running_loop()
        future: asyncio.Future[object] = loop.create_future()
        self._pending[key] = future
        try:
            value = await loader()
        except BaseException as exc:
            if not future.done():
                future.set_exception(exc)
            raise
        else:
            self._values[key] = (time.monotonic() + self.ttl, value)
            if not future.done():
                future.set_result(value)
            return value
        finally:
            self._pending.pop(key, None)

    def invalidate(self, key: str) -> None:
        self._values.pop(key, None)

    def clear(self) -> None:
        self._values.clear()
