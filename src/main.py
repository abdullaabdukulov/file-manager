from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config import app_configs, settings
from src.auth.router import router as auth_router
from src.users.router import router as users_router
from src.files.router import router as files_router


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    """Handle startup and shutdown events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    """Check the health of the application."""
    return {"status": "ok"}
