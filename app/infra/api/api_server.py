from __future__ import annotations

import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

LOGGER = logging.getLogger("api")


def create_app(api_router: APIRouter) -> FastAPI:
    app = FastAPI(
        title="Pirometros API",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )
    app.include_router(api_router)

    @app.exception_handler(SQLAlchemyError)
    async def handle_database_error(_request: Request, error: SQLAlchemyError) -> JSONResponse:
        # Registra so o tipo do erro: a mensagem do driver pode carregar o DSN.
        LOGGER.warning("database error: %s", type(error).__name__)
        return JSONResponse(status_code=503, content={"detail": "banco de dados indisponivel"})

    return app
