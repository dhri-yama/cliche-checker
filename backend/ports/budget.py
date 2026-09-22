"""Port: corpus token-budget policy."""

from __future__ import annotations

from typing import Protocol, Sequence


class BudgetPolicy(Protocol):
    def apply(self, posts: Sequence[str], draft: str) -> list[str]:
        """Return a list of posts that fits the model's state token budget."""
        ...