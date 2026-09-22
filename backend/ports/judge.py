"""Port: the judging model (e.g. TypeSafe Jev or a deterministic stub)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from backend.domain.models import Verdict


@dataclass(frozen=True)
class JudgeAnswers:
    score: float
    verdict: Verdict
    verdict_confidence: float
    saturated: float


class Judge(Protocol):
    def ask(self, state: Mapping[str, Any], questions: Mapping[str, Any]) -> JudgeAnswers:
        """Submit a state + questions to the judge and return typed answers."""
        ...