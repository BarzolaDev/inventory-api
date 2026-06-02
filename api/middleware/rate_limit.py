from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from api.core.rate_limiter import rate_limit

ROUTE_LIMITS = {
    "/users/login": {"POST": {"limit": 5, "window": 60}},
    "/users/register": {"POST": {"limit": 10, "window": 3600}},
    "/users/refresh": {"POST": {"limit": 5, "window": 60}},
}

DEFAULT_LIMITS = {
    "POST": {"limit": 20, "window": 60},
    "PATCH": {"limit": 20, "window": 60},
    "DELETE": {"limit": 5, "window": 60},
    "GET": {"limit": 100, "window": 60},
}

STOCK_LIMIT = {"limit": 10, "window": 60}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path

        if path in ROUTE_LIMITS and method in ROUTE_LIMITS[path]:
            config = ROUTE_LIMITS[path][method]
        elif "/stock" in path and method == "POST":
            config = STOCK_LIMIT
        elif method in DEFAULT_LIMITS:
            config = DEFAULT_LIMITS[method]
        else:
            return await call_next(request)

        try:
            await rate_limit(request, limit=config["limit"], window=config["window"])
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        return await call_next(request)