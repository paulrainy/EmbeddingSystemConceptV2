from __future__ import annotations

"""
Крошечная обёртка над redis.asyncio.Redis.

• Управляет одним-единственным соединением (lru_cache).
• Простые хелперы set_json / get_json с namespace ingest: и TTL.
"""

from functools import lru_cache
from typing import Final

import redis.asyncio as redis
import io, pandas as pd, json

from app.core.config import get_settings

_SETTINGS = get_settings()

# время жизни подготовленного набора (секунд)
DEFAULT_TTL: Final[int] = 3_600  # 1 час


@lru_cache
def get_client() -> redis.Redis:
    """Singleton-клиент Redis, настроенный из config.py."""
    return redis.from_url(
        _SETTINGS.redis_url,
        encoding="utf-8",
        decode_responses=False,  # получаем bytes
    )


async def set_json(key: str, value: str | bytes, *, ttl: int = DEFAULT_TTL) -> None:
    """
    Сохранить JSON-строку под ключом ``ingest:{key}`` с TTL.

    Parameters
    ----------
    key : str
        Часть ключа без namespace (`ingest:` добавляется внутри).
    value : str | bytes
        JSON-payload (обычно результат `df.to_json()`).
    ttl : int, default DEFAULT_TTL
        Время жизни записи в секундах.
    """
    client = get_client()
    await client.setex(f"ingest:{key}", ttl, value)


async def get_json(key: str) -> bytes | None:
    """Вернуть bytes или None, если ключа/TTL уже нет."""
    client = get_client()
    return await client.get(f"ingest:{key}")

async def load_df(job_id: str) -> pd.DataFrame:
    raw = await get_json(job_id)
    if raw is None:
        raise KeyError("expired or wrong id")
    return pd.read_json(io.StringIO(raw.decode()), orient="records")
