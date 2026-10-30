from __future__ import annotations

from fastapi import APIRouter, FastAPI


def create_app(api_router: APIRouter) -> FastAPI:
    app = FastAPI(
        title="Pirometros API",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )
    app.include_router(api_router)
    return app
