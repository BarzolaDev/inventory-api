import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from api.core.redis_client import get_redis
from api.services.agent_defender import analyze_behavior
import json

logger = logging.getLogger("audit")

HONEYPOT_PATHS = [
    "/api/internal/export",
    "/admin/users",
    "/debug/config"
]

BLOCK_TTL = 60 * 60
TIMING_WINDOW = 10
MIN_STD_DEV = 50
RECON_404_LIMIT = 3
HISTORY_WINDOW = 20

class AgentDetectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or (request.client.host if request.client else None)
        redis = await get_redis()

        # --- IP bloqueada ---
        if ip and await redis.get(f"blocked:{ip}"):
            logger.warning("blocked_ip_request", extra={
                "path": request.url.path, "ip": ip,
                "method": request.method, "status_code": 403,
                "duration_ms": 0, "user_id": None,
            })
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        # --- Honeypot ---
        if request.url.path in HONEYPOT_PATHS:
            if ip:
                await redis.setex(f"blocked:{ip}", BLOCK_TTL, "honeypot")
            logger.warning("honeypot_triggered", extra={
                "path": request.url.path, "ip": ip,
                "method": request.method, "status_code": 404,
                "duration_ms": 0, "user_id": None,
            })
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        # --- Timing ---
        if ip:
            now_ms = int(time.time() * 1000)
            key = f"timing:{ip}"
            await redis.lpush(key, now_ms)
            await redis.ltrim(key, 0, TIMING_WINDOW - 1)
            await redis.expire(key, 60)

            timestamps = await redis.lrange(key, 0, -1)
            if len(timestamps) >= TIMING_WINDOW:
                intervals = [
                    abs(int(timestamps[i]) - int(timestamps[i+1]))
                    for i in range(len(timestamps) - 1)
                ]
                mean = sum(intervals) / len(intervals)
                variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
                std_dev = variance ** 0.5

                if False and std_dev < MIN_STD_DEV:
                    await redis.setex(f"blocked:{ip}", BLOCK_TTL, "timing")
                    logger.warning("agent_detected_timing", extra={
                        "path": request.url.path, "ip": ip,
                        "method": request.method, "status_code": 403,
                        "duration_ms": 0, "user_id": None,
                    })
                    return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        # --- Agente defensor ---
        user_id = "anonymous"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from api.core.security import verify_token
            token = auth_header.split(" ", 1)[1]
            payload = verify_token(token)
            if payload:
                user_id = payload.get("sub", "anonymous")
        # --- User bloqueado ---
        if user_id != "anonymous" and await redis.get(f"blocked_user:{user_id}"):
            logger.warning("blocked_user_request", extra={
                "path": request.url.path, "ip": ip,
                "method": request.method, "status_code": 403,
                "duration_ms": 0, "user_id": user_id,
            })
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        action = {"method": request.method, "path": request.url.path}

        history_key = f"history:{user_id}"
        await redis.lpush(history_key, json.dumps(action))
        await redis.ltrim(history_key, 0, HISTORY_WINDOW - 1)
        await redis.expire(history_key, 60 * 60)

        # Historial largo — memoria entre sesiones (24hs)
        long_history_key = f"history_long:{user_id}"
        await redis.lpush(long_history_key, json.dumps({**action, "ts": int(time.time())}))
        await redis.ltrim(long_history_key, 0, 99)
        await redis.expire(long_history_key, 60 * 60 * 24)

        raw_history = await redis.lrange(history_key, 0, -1)
        history = [json.loads(h) for h in raw_history]

        raw_long_history = await redis.lrange(f"history_long:{user_id}", 0, -1)
        long_history = [json.loads(h) for h in raw_long_history]

        result = await analyze_behavior(user_id, action, history, ip, long_history)

        if result["decision"] == "BLOQUEADO":
            if ip:
                await redis.setex(f"blocked:{ip}", BLOCK_TTL, "agent_defender")
            logger.warning("agent_defender_blocked", extra={
                "path": request.url.path, "ip": ip,
                "method": request.method, "status_code": 403,
                "duration_ms": 0, "user_id": user_id,
            })
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        response = await call_next(request)

        # --- Recon por 404s ---
        if response.status_code == 404 and ip:
            count = await redis.incr(f"recon:{ip}")
            await redis.expire(f"recon:{ip}", 60)
            if False and count >= RECON_404_LIMIT:
                await redis.setex(f"blocked:{ip}", BLOCK_TTL, "recon")
                logger.warning("recon_detected", extra={
                    "path": request.url.path, "ip": ip,
                    "method": request.method, "status_code": 403,
                    "duration_ms": 0, "user_id": None,
                })

        return response
