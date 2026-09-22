"""Request/response DTOs for the HTTP API (validation at the edge)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    draft: str = Field(min_length=1, max_length=280, description="The user's draft post.")
    tweets: list[str] = Field(
        default_factory=list,
        max_length=10_000,
        description="Tweet texts scraped from the open hashtag page.",
    )


class CheckResponse(BaseModel):
    originality: int = Field(ge=0, le=100)
    verdict: Literal["rework", "refine", "publish"]
    verdict_confidence: float = Field(ge=0.0, le=1.0)
    saturated: float = Field(ge=0.0, le=1.0)
    jev_ms: float


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    mode: str