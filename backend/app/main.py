import asyncio
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.qdrant_client import ensure_qdrant_collections, qdrant_health
from app.core.redis_client import redis_health
from app.api.router import api_router
from app.realtime.redis_listener import listen_for_realtime_messages
from app.realtime.routes import router as websocket_router
from app.ai.service import ZenFitAIService
from app.ai.registry import registry

app = FastAPI(title=settings.app_name)
Path(settings.local_upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.local_upload_dir), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.backend_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    ensure_qdrant_collections()
    registry.prewarm()
    app.state.realtime_stop_event = asyncio.Event()
    app.state.realtime_task = asyncio.create_task(listen_for_realtime_messages(app.state.realtime_stop_event))


@app.on_event("shutdown")
async def shutdown() -> None:
    stop_event = getattr(app.state, "realtime_stop_event", None)
    realtime_task = getattr(app.state, "realtime_task", None)
    if stop_event and realtime_task:
        stop_event.set()
        await realtime_task


@app.get(f"{settings.api_v1_prefix}/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "redis": "ok" if redis_health() else "error",
        "qdrant": "ok" if qdrant_health() else "error",
        "ai": ZenFitAIService().health(),
    }


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(websocket_router)
