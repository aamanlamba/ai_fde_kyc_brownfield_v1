from __future__ import annotations

from src.adapters.sample_repository import load_sidecar
from src.ports import ExtractionProvider


class SidecarTextExtractor(ExtractionProvider):
    def extract(self, document_id: str) -> str:
        return load_sidecar(document_id)


def extract_text(document_id: str) -> str:
    return load_sidecar(document_id)
