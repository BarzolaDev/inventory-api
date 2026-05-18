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

    if redis is None:
        return  # Redis no disponible, skip rate limiting

    client_id = request.headers.get("Authorization") or request.client.host
    key = f"rate_limit:{request.url.path}:{client_id}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window)  

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Demasiados intentos. Límite: {limit} por {window} segundos."
        )