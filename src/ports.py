from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol, runtime_checkable


@dataclass
class FieldValue:
    raw: str | None = None
    value: str | None = None
    confidence: float = 1.0


@dataclass
class ExtractionResult:
    document_id: str
    fields: dict[str, FieldValue] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    raw_text: str = ""
    adapter_name: str = ""
    adapter_version: str = ""


class ExtractionUnavailable(RuntimeError):
    pass


@runtime_checkable
class ExtractionProvider(Protocol):
    def extract(self, document_id: str) -> ExtractionResult:
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
    def signals(self, extraction: ExtractionResult) -> list[str]:
        ...
