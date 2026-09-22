"""Port: tweet text cleaning."""

from __future__ import annotations

from typing import Protocol, Sequence


class Cleaner(Protocol):
    def clean(self, tweets: Sequence[str]) -> list[str]:
        """Return cleaned, deduplicated tweet texts from the given inputs."""
        ...