"""Port: builds typed questions for the judge from a rubric."""

from __future__ import annotations

from typing import Protocol

from backend.domain.rubrics import Rubric


class QuestionFactory(Protocol):
    def build(self, rubric: Rubric) -> dict:
        """Return the questions mapping understood by the underlying judge."""
        ...