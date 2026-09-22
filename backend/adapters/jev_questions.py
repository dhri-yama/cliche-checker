"""Builds TypeSafe typed questions (Score / Choice / Noul) from a rubric."""

from __future__ import annotations

from typesafe_sdk import Choice, Noul, Score

from backend.domain.rubrics import Rubric
from backend.ports.question_factory import QuestionFactory


class JevQuestionFactory(QuestionFactory):
    def build(self, rubric: Rubric) -> dict:
        return {
            "originality": Score(
                instructions=(
                    "Rate how original the DRAFT is relative to the MARKET_CONTEXT. "
                    "The MARKET_CONTEXT is a sample of the top posts dominating this hashtag: "
                    "ideas and phrasings that recur across those posts define the cliche baseline. "
                    "Compare the idea, the framing, and the phrasings used in the DRAFT. "
                    "A draft that re-says anything already common in the context should score low, "
                    "regardless of how well it is written."
                ),
                criteria=rubric.originality_levels,
            ),
            "verdict": Choice(
                instructions=(
                    "Which action does the DRAFT deserve given how much it repeats the MARKET_CONTEXT? "
                    "Be strict: writing quality does not rescue an idea the market has already hammered."
                ),
                criteria=rubric.verdict_criteria,
            ),
            "saturated": Noul(instructions=rubric.saturated_instruction),
        }