"""Judge adapter backed by the TypeSafe Jev system_one API."""

from __future__ import annotations

from typing import Any, Mapping

from typesafe_sdk import TypeSafeClient

from backend.domain.exceptions import JudgeError, MissingApiKeyError
from backend.domain.models import Verdict
from backend.ports.judge import Judge, JudgeAnswers


class JevJudge(Judge):
    def __init__(self, api_key: str | None, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def ask(self, state: Mapping[str, Any], questions: Mapping[str, Any]) -> JudgeAnswers:
        if not self._api_key:
            raise MissingApiKeyError()

        try:
            with TypeSafeClient(api_key=self._api_key) as client:
                response = client.system_one(state=state, questions=questions, model=self._model)
        except Exception as exc:  # noqa: BLE001 - surface any judge failure uniformly
            raise JudgeError(f"Jev request failed: {exc}") from exc

        return JudgeAnswers(
            score=response.scores["originality"].score,
            verdict=Verdict(response.choices["verdict"].choice),
            verdict_confidence=response.choices["verdict"].confidence,
            saturated=response.nouls["saturated"].noul,
        )