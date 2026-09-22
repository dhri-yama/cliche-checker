"""The Jev grading rubric: score levels, verdict options, and corpus framing."""

from __future__ import annotations

from dataclasses import dataclass

CORPUS_NOTE = (
    "MARKET_CONTEXT lists the top posts currently dominating this hashtag. "
    "Ideas, framings, and phrasings that recur across multiple posts are the cliche baseline. "
    "Judge the DRAFT against that baseline: a draft that repeats a recurring theme is cliche."
)

ORIGINALITY_LEVELS = [
    "Overdone cliche: the draft restates a sentiment or phrasing that recurs across multiple MARKET_CONTEXT posts.",
    "Saturated: a familiar idea with only superficial rewording, already repeated in the MARKET_CONTEXT.",
    "Familiar but personal: a known topic stated with a specific first-hand detail or uncommon example not seen in the context posts.",
    "Fresh angle: a recognizable topic approached from a viewpoint rarely seen across the MARKET_CONTEXT.",
    "Genuinely distinctive: a take or framing that no MARKET_CONTEXT post touches.",
]

VERDICT_CRITERIA = {
    "rework": "The draft repeats a theme already hammered across the MARKET_CONTEXT; its core idea needs to change.",
    "refine": "The draft partially overlaps the MARKET_CONTEXT but can be saved by sharpening framing, detail, or example.",
    "publish": "The draft is original enough relative to the MARKET_CONTEXT; ship it as-is.",
}


@dataclass(frozen=True)
class Rubric:
    corpus_note: str
    originality_levels: tuple[str, ...]
    verdict_criteria: dict[str, str]
    saturated_instruction: str

    @property
    def score_top(self) -> int:
        return len(self.originality_levels) - 1

    @classmethod
    def default(cls) -> "Rubric":
        return cls(
            corpus_note=CORPUS_NOTE,
            originality_levels=tuple(ORIGINALITY_LEVELS),
            verdict_criteria=dict(VERDICT_CRITERIA),
            saturated_instruction="Does the DRAFT re-say any idea, framing, or phrasing that already recurs across multiple MARKET_CONTEXT posts? Answer yes only when the overlap is meaningful, not merely thematic.",
        )