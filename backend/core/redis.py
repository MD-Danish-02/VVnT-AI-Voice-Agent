from __future__ import annotations

import logging
from typing import Optional

import redis.asyncio as aioredis

from core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[aioredis.Redis] = None


def get_redis_client() -> aioredis.Redis:
    """Return a singleton async Redis client instance.

    The client manages an underlying connection pool automatically.
    """
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
    return redis_client


async def ping_redis() -> bool:
    """Lightweight internal connectivity check that pings the Redis server.

    Returns True if healthy, False if unavailable or unreachable.
    Does not raise exceptions to ensure API resilience.
    """
    try:
        client = get_redis_client()
        return bool(await client.ping())
    except Exception as exc:
        logger.warning("Redis connectivity check failed: %s", exc)
        return False


async def close_redis() -> None:
    """Cleanly close the async Redis client and underlying connection pool."""
    global redis_client
    if redis_client is not None:
        try:
            await redis_client.aclose()
        except Exception as exc:
            logger.warning("Error closing Redis client: %s", exc)
        finally:
            redis_client = None
