"""Draft grading endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.api.routes.health_controller import get_container
from backend.api.schemas import CheckRequest, CheckResponse
from backend.container import Container
from backend.domain.exceptions import DomainError
from backend.domain.models import Draft, TweetCorpus


class CheckController:
    router: APIRouter = APIRouter(tags=["check"])

    @staticmethod
    @router.post("/check", response_model=CheckResponse)
    def check(payload: CheckRequest, container: Container = Depends(get_container)) -> CheckResponse:
        service = container.grading_service()
        try:
            result = service.grade(Draft(payload.draft), TweetCorpus(tuple(payload.tweets)))
        except DomainError as exc:
            raise _http_error(exc) from exc
        return CheckResponse(**result.to_dict())


def _http_error(exc: DomainError):
    message = str(exc)
    if message.startswith("Market corpus is empty"):
        status = 422
    elif message.startswith("TYPESAFE_API_KEY"):
        status = 503
    else:
        status = 502
    return HTTPException(status_code=status, detail=message)