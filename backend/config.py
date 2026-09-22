"""Configuration for the cliche-checker backend."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum

from dotenv import load_dotenv

load_dotenv()


class RunMode(str, Enum):
    LIVE = "live"
    STUB = "stub"


@dataclass(frozen=True)
class Settings:
    typesafe_api_key: str | None
    model: str = "jev-latest"
    max_state_tokens: int = 30_000
    run_mode: RunMode = RunMode.LIVE
    host: str = "127.0.0.1"
    port: int = 8000

    @property
    def has_key(self) -> bool:
        return bool(self.typesafe_api_key)

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("TYPESAFE_API_KEY") or None
        run_mode = RunMode(os.getenv("RUN_MODE", "live").lower() or RunMode.LIVE)
        return cls(
            typesafe_api_key=api_key,
            model=os.getenv("TYPESAFE_MODEL", "jev-latest"),
            max_state_tokens=int(os.getenv("MAX_STATE_TOKENS", "30000")),
            run_mode=run_mode,
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8000")),
        )


def default_settings() -> Settings:
    """Cached default settings so tests and the app share one instance."""
    return Settings.from_env()