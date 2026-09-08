from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from api.v1.appointments import router as appointments_router
from api.v1.auth import router as auth_router
from api.v1.calls import router as calls_router
from api.v1.leads import router as leads_router
from core.config import settings
from core.redis import close_redis, ping_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Optional startup connectivity check (non-fatal if Redis is unavailable)
    try:
        redis_ok = await ping_redis()
        if redis_ok:
            logger.info("Redis connection established successfully")
        else:
            logger.warning("Redis is currently unavailable; proceeding without active Redis connection")
    except Exception as exc:
        logger.warning("Redis startup check encountered an error: %s", exc)

    yield

    # Clean shutdown of Redis client and connection pool
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(leads_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(calls_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }