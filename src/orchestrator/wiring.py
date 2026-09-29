from __future__ import annotations

from typing import Any

from src.adapters.clocks import SystemClock
from src.adapters.file_policy_source import FilePolicySource
from src.adapters import sample_repository as _sample_repository
from src.adapters.sidecar_text import SidecarAdapter
from src.adapters.tamper_marker import MarkerSignal
from src.ports import Clock, ExtractionProvider, PolicySource, TamperSignalProvider

_default_policy_source: PolicySource = FilePolicySource()
_default_provider: ExtractionProvider = SidecarAdapter(_default_policy_source)
_default_clock: Clock = SystemClock()
_default_tamper_provider: TamperSignalProvider = MarkerSignal()


def get_extraction_provider() -> ExtractionProvider:
    return _default_provider


def set_extraction_provider(provider: ExtractionProvider) -> None:
    global _default_provider
    _default_provider = provider


def get_policy_source() -> PolicySource:
    return _default_policy_source


def set_policy_source(source: PolicySource) -> None:
    global _default_policy_source
    _default_policy_source = source


def get_policy() -> dict[str, Any]:
    source = get_policy_source()
    if hasattr(source, 'get_policy'):
        return source.get_policy()
    if hasattr(source, 'load_policy'):
        return source.load_policy()
    if callable(source):
        return source()
    return dict(source)


def get_clock() -> Clock:
    return _default_clock


def set_clock(clock: Clock) -> None:
    global _default_clock
    _default_clock = clock


def get_tamper_provider() -> TamperSignalProvider:
    return _default_tamper_provider


def set_tamper_provider(provider: TamperSignalProvider) -> None:
    global _default_tamper_provider
    _default_tamper_provider = provider


def load_application(case_id: str) -> dict[str, Any]:
    return _sample_repository.load_application(case_id)


def load_ground_truth(document_id: str) -> dict[str, Any]:
    return _sample_repository.load_ground_truth(document_id)


def load_json(folder: str, ident: str) -> dict[str, Any]:
    return _sample_repository.load_json(folder, ident)


def load_sidecar(document_id: str) -> str:
    return _sample_repository.load_sidecar(document_id)


def list_cases() -> list[dict[str, Any]]:
    return _sample_repository.list_cases()


def safe_id(value: str) -> str:
    return _sample_repository.safe_id(value)
