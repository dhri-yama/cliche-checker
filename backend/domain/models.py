"""Domain value objects for cliche-checker."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    REWORK = "rework"
    REFINE = "refine"
    PUBLISH = "publish"


@dataclass(frozen=True)
class Draft:
    text: str


@dataclass(frozen=True)
class TweetCorpus:
    posts: tuple[str, ...]

    def __init__(self, posts: tuple[str, ...]):
        object.__setattr__(self, "posts", tuple(posts))


@dataclass(frozen=True)
class GradeResult:
    originality: int
    verdict: Verdict
    verdict_confidence: float
    saturated: float
    jev_ms: float

    def to_dict(self) -> dict:
        return {
            "originality": self.originality,
            "verdict": self.verdict.value,
            "verdict_confidence": round(self.verdict_confidence, 4),
            "saturated": round(self.saturated, 4),
            "jev_ms": round(self.jev_ms, 1),
        }