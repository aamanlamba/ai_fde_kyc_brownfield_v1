from __future__ import annotations

from src.ports import ExtractionResult, TamperSignalProvider


class MarkerSignal(TamperSignalProvider):
    """SIMULATED marker adapter; this is not image forensics."""

    def signals(self, extraction: ExtractionResult) -> list[str]:
        if 'ALTERED_TEXT_REGION_DETECTED' in extraction.raw_text:
            return ['SUSPECTED_TAMPERING']
        return []