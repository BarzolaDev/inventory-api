import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from api.core.security import verify_token

logger = logging.getLogger("audit")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # --- Extraer user_id del JWT si existe ---
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            payload = verify_token(token)
            if payload:
                user_id = payload.get("sub")

        # --- Procesar request ---
        response = await call_next(request)

        # --- Calcular duración ---
        duration_ms = round((time.time() - start_time) * 1000)

        # --- Log estructurado ---
        logger.info(
            "request",
            extra={
                "user_id": user_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "ip": request.client.host if request.client else None,
            },
        )

        return response