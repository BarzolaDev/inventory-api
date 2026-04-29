from fastapi import Request, HTTPException, Depends
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

    # Identificar quién hace el request
    # Si viene con JWT usamos eso, si no, la IP
    client_id = request.headers.get("Authorization") or request.client.host
    key = f"rate_limit:{request.url.path}:{client_id}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window)  # TTL solo la primera vez

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Demasiados intentos. Límite: {limit} por {window} segundos."
        )