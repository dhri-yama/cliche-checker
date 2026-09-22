"""Deterministic judge for development and tests (LSP: same contract as JevJudge)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.domain.models import Verdict
from backend.ports.judge import Judge, JudgeAnswers


@dataclass
class StubJudge(Judge):
    score: float = 3.0
    verdict: Verdict = Verdict.PUBLISH
    verdict_confidence: float = 0.9
    saturated: float = 0.1

    def ask(self, state: Mapping[str, Any], questions: Mapping[str, Any]) -> JudgeAnswers:
        return JudgeAnswers(
            score=self.score,
            verdict=self.verdict,
            verdict_confidence=self.verdict_confidence,
            saturated=self.saturated,
        )