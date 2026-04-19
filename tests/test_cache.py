import asyncio

import pytest

from bot.services.cache import TTLCache


@pytest.mark.asyncio
async def test_cache_hits_on_second_call() -> None:
    cache = TTLCache(ttl_seconds=10)
    calls = {"n": 0}

    async def load() -> int:
        calls["n"] += 1
        return 42

    a = await cache.get_or_set("k", load)
    b = await cache.get_or_set("k", load)
    assert a == 42 and b == 42
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_cache_expires() -> None:
    cache = TTLCache(ttl_seconds=0.01)
    await cache.get_or_set("k", _answer(1))
    await asyncio.sleep(0.05)
    value = await cache.get_or_set("k", _answer(2))
    assert value == 2


@pytest.mark.asyncio
async def test_concurrent_requests_coalesce() -> None:
    cache = TTLCache(ttl_seconds=10)
    calls = {"n": 0}
    gate = asyncio.Event()

    async def load() -> str:
        calls["n"] += 1
        await gate.wait()
        return "v"

    task_a = asyncio.create_task(cache.get_or_set("k", load))
    task_b = asyncio.create_task(cache.get_or_set("k", load))
    await asyncio.sleep(0.01)  # let both enter
    gate.set()
    a, b = await asyncio.gather(task_a, task_b)
    assert a == "v" and b == "v"
    assert calls["n"] == 1


def _answer(value: int):  # type: ignore[no-untyped-def]
    async def load() -> int:
        return value

    return load
