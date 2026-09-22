"""Assembles the judge state object (corpus note + numbered posts + draft)."""

from __future__ import annotations

from typing import Mapping, Sequence

from backend.domain.models import Draft, TweetCorpus
from backend.ports.budget import BudgetPolicy


class StateBuilder:
    def __init__(self, corpus_note: str, budget: BudgetPolicy) -> None:
        self._corpus_note = corpus_note
        self._budget = budget

    def build(self, draft: Draft, corpus: TweetCorpus) -> Mapping[str, object]:
        posts = self._budget.apply(corpus.posts, draft.text)
        return {
            "corpus_note": self._corpus_note,
            "market_context": [f"{i}. {post}" for i, post in enumerate(posts, start=1)],
            "draft": draft.text,
        }