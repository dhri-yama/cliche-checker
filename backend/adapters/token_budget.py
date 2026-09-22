"""Concrete token-budget policies for the state assembly."""

from __future__ import annotations

from typing import Sequence

from backend.ports.budget import BudgetPolicy


def _est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class TokenSamplingBudget(BudgetPolicy):
    """Evenly samples the corpus down to fit a configured token ceiling."""

    def __init__(self, max_state_tokens: int, overhead_tokens: int = 300) -> None:
        self._max_state_tokens = max_state_tokens
        self._overhead_tokens = overhead_tokens

    def apply(self, posts: Sequence[str], draft: str) -> list[str]:
        overhead = self._overhead_tokens + _est_tokens(draft)
        total = overhead + sum(_est_tokens(p) for p in posts)
        if total <= self._max_state_tokens:
            return list(posts)

        body = max(1, total - overhead)
        max_posts = max(1, int(len(posts) * (self._max_state_tokens - overhead) / body))
        step = len(posts) / max_posts
        return [posts[int(i * step)] for i in range(max_posts)]


class PassthroughBudget(BudgetPolicy):
    """Never samples; used when the corpus is known to fit."""

    def apply(self, posts: Sequence[str], draft: str) -> list[str]:
        return list(posts)