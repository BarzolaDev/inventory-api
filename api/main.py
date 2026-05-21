from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.middleware.rate_limit_middleware import RateLimitMiddleware
from api.middleware.logging_middleware import LoggingMiddleware
from api.routes import product, user
from api.core.redis_client import init_redis, close_redis
import api.core.logging  

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def remove_server_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["server"] = "unknown"
    return response

app.add_middleware(LoggingMiddleware)
#app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(user.router, prefix="/users", tags=["Users"])