from __future__ import annotations

from src.adapters.sidecar_text import SidecarAdapter
from src.ports import ExtractionProvider

_default_provider: ExtractionProvider = SidecarAdapter()


def get_extraction_provider() -> ExtractionProvider:
    return _default_provider


def set_extraction_provider(provider: ExtractionProvider) -> None:
    global _default_provider
    _default_provider = provider
