"""Application service: orchestrates cleaning, budgeting, state, and judging."""

from __future__ import annotations

import time

from backend.domain.exceptions import EmptyCorpusError
from backend.domain.models import Draft, GradeResult, TweetCorpus
from backend.domain.rubrics import Rubric
from backend.ports.cleaner import Cleaner
from backend.ports.judge import Judge
from backend.ports.question_factory import QuestionFactory


class GradingService:
    def __init__(
        self,
        cleaner: Cleaner,
        rubric: Rubric,
        state_builder,
        question_factory: QuestionFactory,
        judge: Judge,
    ) -> None:
        self._cleaner = cleaner
        self._rubric = rubric
        self._state_builder = state_builder
        self._question_factory = question_factory
        self._judge = judge

    def grade(self, draft: Draft, corpus: TweetCorpus) -> GradeResult:
        posts = self._cleaner.clean(corpus.posts)
        if not posts:
            raise EmptyCorpusError()

        state = self._state_builder.build(draft, TweetCorpus(tuple(posts)))
        questions = self._question_factory.build(self._rubric)

        started = time.perf_counter()
        answers = self._judge.ask(state, questions)
        elapsed_ms = (time.perf_counter() - started) * 1000

        originality = round(100 * answers.score / self._rubric.score_top)
        return GradeResult(
            originality=clamp(originality, 0, 100),
            verdict=answers.verdict,
            verdict_confidence=answers.verdict_confidence,
            saturated=answers.saturated,
            jev_ms=elapsed_ms,
        )


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))