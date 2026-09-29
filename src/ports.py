from __future__ import annotations

from datetime import date
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ExtractionProvider(Protocol):
    def extract(self, document_id: str) -> str:
        ...


@runtime_checkable
class PolicySource(Protocol):
    def load_policy(self) -> dict[str, Any]:
        ...


@runtime_checkable
class EvidenceStore(Protocol):
    def save(self, key: str, payload: dict[str, Any]) -> None:
        ...


@runtime_checkable
class TokenVerifier(Protocol):
    def verify(self, token: str) -> bool:
        ...


@runtime_checkable
class Clock(Protocol):
    def today(self) -> date:
        ...


@runtime_checkable
class ReviewQueue(Protocol):
    def enqueue(self, review_id: str, payload: dict[str, Any]) -> None:
        ...


@runtime_checkable
class TamperSignalProvider(Protocol):
    def signal(self, document_id: str) -> bool:
        ...
