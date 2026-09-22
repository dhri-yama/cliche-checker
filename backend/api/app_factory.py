"""FastAPI application factory (composition root for the web layer)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.check_controller import CheckController
from backend.api.routes.health_controller import HealthController
from backend.config import Settings, default_settings
from backend.container import Container


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or default_settings()
    container = Container(settings)

    app = FastAPI(title="cliche-checker", version="0.1.0")
    app.state.container = container
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "chrome-extension://*",
            f"http://{settings.host}:{settings.port}",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.include_router(HealthController.router)
    app.include_router(CheckController.router)
    return app


app = create_app()