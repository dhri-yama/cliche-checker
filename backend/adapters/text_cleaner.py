"""Concrete cleaners for tweet text (tweet corpus -> clean corpus)."""

from __future__ import annotations

import re
from typing import Sequence

from backend.ports.cleaner import Cleaner

_URL_RE = re.compile(r"https?://\S+")
_HANDLE_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"\B#\w+")


class NoiseFilterCleaner(Cleaner):
    """Drops retweets and URL-only or symbol-only posts."""

    def clean(self, tweets: Sequence[str]) -> list[str]:
        kept: list[str] = []
        for tweet in tweets:
            stripped = tweet.strip()
            if not stripped or stripped.startswith("RT @") or stripped.startswith("http"):
                continue
            if not any(ch.isalnum() for ch in stripped):
                continue
            kept.append(stripped)
        return kept


class LightTextCleaner(Cleaner):
    """Strips URLs, @mentions, and hashtags; collapses whitespace."""

    def clean(self, tweets: Sequence[str]) -> list[str]:
        cleaned: list[str] = []
        for tweet in tweets:
            out = _URL_RE.sub("", tweet)
            out = _HANDLE_RE.sub("", out)
            out = _HASHTAG_RE.sub("", out)
            out = " ".join(out.split())
            if out and any(ch.isalnum() for ch in out):
                cleaned.append(out)
        return cleaned


class DedupeCleaner(Cleaner):
    """Normalizes whitespace, drops empties, and keeps first-seen order."""

    def clean(self, tweets: Sequence[str]) -> list[str]:
        seen: set[str] = set()
        kept: list[str] = []
        for tweet in tweets:
            normalized = " ".join(tweet.split())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            kept.append(normalized)
        return kept


class CompositeCleaner(Cleaner):
    """Applies a chain of cleaners in order (SRP + OCP: add steps freely)."""

    def __init__(self, cleaners: Sequence[Cleaner]) -> None:
        self._cleaners = list(cleaners)

    def clean(self, tweets: Sequence[str]) -> list[str]:
        result: list[str] = list(tweets)
        for cleaner in self._cleaners:
            result = cleaner.clean(result)
        return result


def default_cleaner() -> Cleaner:
    return CompositeCleaner([NoiseFilterCleaner(), LightTextCleaner(), DedupeCleaner()])