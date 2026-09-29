from __future__ import annotations

from src.ports import ExtractionProvider, ExtractionResult, ExtractionUnavailable, FieldValue


class MockAdapter(ExtractionProvider):
    def __init__(self, text: str | None = None, *, exc: Exception | None = None):
        self._text = text
        self._exc = exc

    def extract(self, document_id: str) -> ExtractionResult:
        if self._exc is not None:
            raise self._exc
        if self._text is None:
            raise ExtractionUnavailable(document_id)
        raw_text = self._text
        fields: dict[str, FieldValue] = {}
        for line in raw_text.splitlines():
            label, sep, value = line.partition(':')
            if not sep:
                continue
            key = label.strip().lower().replace(' ', '_')
            fields[key] = FieldValue(raw=value.strip(), value=value.strip(), confidence=1.0)
        return ExtractionResult(
            document_id=document_id,
            fields=fields,
            missing_fields=[],
            warnings=[],
            raw_text=raw_text,
            adapter_name='MockAdapter',
            adapter_version='1.0',
        )
