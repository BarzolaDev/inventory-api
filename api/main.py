from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.logging import LoggingMiddleware
from api.middleware.agent_detect import AgentDetectMiddleware
from api.routes import product, user, decisions
from api.core.redis_client import init_redis, close_redis
from api.core.settings import settings
import api.core.logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid request"}
    )

@app.middleware("http")
async def remove_server_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["server"] = "unknown"
    return response

app.add_middleware(AgentDetectMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_headers=["Authorization", "Content-Type"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(decisions.router, prefix="/decisions", tags=["Decisions"])
#app.mount('/static', StaticFiles(directory='static'), name='static')
