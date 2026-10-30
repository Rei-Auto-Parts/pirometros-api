from __future__ import annotations

from collections.abc import Callable

import uvicorn
from fastapi import FastAPI


class ApiEntry:
    def __init__(
        self, app: FastAPI, host: str, port: int, before_start: Callable[[], None]
    ) -> None:
        self._app = app
        self._host = host
        self._port = port
        self._before_start = before_start

    def run(self) -> None:
        self._before_start()
        uvicorn.run(self._app, host=self._host, port=self._port)
