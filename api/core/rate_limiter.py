import random
from fastapi import Request, HTTPException
from redis.asyncio import Redis
from api.core.redis_client import get_redis

async def rate_limit(
    request: Request,
    limit: int,
    window: int,
    redis: Redis = None
):
    if redis is None:
        redis = await get_redis()
    if redis is None:
        return  # Redis no disponible, skip rate limiting

    client_id = request.headers.get("CF-Connecting-IP") or request.headers.get("Authorization") or request.client.host
    key = f"rate_limit:{request.url.path}:{client_id}"
    block_key = f"rate_block:{request.url.path}:{client_id}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window)

    if count > limit:
        block_count = int(await redis.get(block_key) or 0)
        backoff = min(window * (2 ** block_count), 3600)
        jitter = random.randint(0, backoff // 2)
        actual_window = backoff + jitter

        await redis.incr(block_key)
        await redis.expire(block_key, 86400)  # historial de bloqueos dura 24hs

        raise HTTPException(
            status_code=429,
            detail=f"Demasiados intentos. Reintentá en {actual_window} segundos."
        )