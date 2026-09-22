"""Composition root: wires concretions into the GradingService (DIP)."""

from __future__ import annotations

from backend.adapters.jev_judge import JevJudge
from backend.adapters.jev_questions import JevQuestionFactory
from backend.adapters.state_builder import StateBuilder
from backend.adapters.stub_judge import StubJudge
from backend.adapters.text_cleaner import default_cleaner
from backend.adapters.token_budget import TokenSamplingBudget
from backend.config import RunMode, Settings, default_settings
from backend.domain.rubrics import Rubric
from backend.services.grading_service import GradingService


class Container:
    """Builds the application object graph."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or default_settings()
        self._rubric: Rubric | None = None
        self._service: GradingService | None = None

    @property
    def settings(self) -> Settings:
        return self._settings

    def rubric(self) -> Rubric:
        if self._rubric is None:
            self._rubric = Rubric.default()
        return self._rubric

    def grading_service(self) -> GradingService:
        if self._service is None:
            judge = self._build_judge()
            budget = TokenSamplingBudget(self._settings.max_state_tokens)
            state_builder = StateBuilder(self.rubric().corpus_note, budget)
            self._service = GradingService(
                cleaner=default_cleaner(),
                rubric=self.rubric(),
                state_builder=state_builder,
                question_factory=JevQuestionFactory(),
                judge=judge,
            )
        return self._service

    def _build_judge(self):
        if self._settings.run_mode is RunMode.STUB:
            return StubJudge()
        return JevJudge(api_key=self._settings.typesafe_api_key, model=self._settings.model)