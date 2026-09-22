"""Domain and application exceptions."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for cliche-checker domain errors."""


class MissingApiKeyError(DomainError):
    def __init__(self) -> None:
        super().__init__("TYPESAFE_API_KEY is not set; add it to your .env file or run in stub mode.")


class EmptyCorpusError(DomainError):
    def __init__(self) -> None:
        super().__init__("Market corpus is empty after cleaning; provide tweet text to grade against.")


class JudgeError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)