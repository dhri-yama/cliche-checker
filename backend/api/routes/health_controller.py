"""Health endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.api.schemas import HealthResponse
from backend.container import Container


def get_container(request: Request) -> Container:
    return request.app.state.container


class HealthController:
    router: APIRouter = APIRouter(tags=["health"])

    @staticmethod
    @router.get("/health", response_model=HealthResponse)
    def health(container: Container = Depends(get_container)) -> HealthResponse:
        return HealthResponse(status="ok", mode=container.settings.run_mode.value)