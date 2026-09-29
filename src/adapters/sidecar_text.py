from __future__ import annotations

import re

from src.adapters.sample_repository import load_sidecar
from src.adapters.file_policy_source import FilePolicySource
from src.ports import ExtractionProvider, ExtractionResult, FieldValue


def _normalise_label(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip()).lower()


_CANONICAL_FIELDS = {
    'document type': 'document_type',
    'document_type': 'document_type',
    'name': 'full_name',
    'full_name': 'full_name',
    'dob': 'date_of_birth',
    'date_of_birth': 'date_of_birth',
    'document no': 'document_number',
    'document_number': 'document_number',
    'issue date': 'issue_date',
    'issue_date': 'issue_date',
    'expiry date': 'expiry_date',
    'expiry_date': 'expiry_date',
    'address': 'address',
    'nationality': 'nationality',
}


class SidecarAdapter(ExtractionProvider):
    adapter_name = 'SidecarAdapter'
    adapter_version = '1.0'

    def __init__(self, policy_source: FilePolicySource | None = None):
        self._policy_source = policy_source or FilePolicySource()

    def _label_aliases(self) -> dict[str, str]:
        aliases: dict[str, str] = {}
        policy = self._policy_source.get_policy()
        for canonical, values in policy.get('label_aliases', {}).items():
            if not isinstance(values, list):
                continue
            field_name = _CANONICAL_FIELDS.get(_normalise_label(str(canonical)), canonical)
            for alias in [canonical, *values]:
                aliases[_normalise_label(str(alias))] = field_name
        for canonical, alias in {
            'document_type': 'document type',
            'full_name': 'name',
            'date_of_birth': 'dob',
            'document_number': 'document no',
            'issue_date': 'issue date',
            'expiry_date': 'expiry date',
            'address': 'address',
            'nationality': 'nationality',
        }.items():
            aliases[_normalise_label(alias)] = canonical
        return aliases

    def extract(self, document_id: str) -> ExtractionResult:
        raw_text = load_sidecar(document_id)
        fields: dict[str, FieldValue] = {}
        warnings: list[str] = []
        alias_map = self._label_aliases()
        mandatory = self._policy_source.get_policy().get('mandatory_fields', [])
        for line in raw_text.splitlines():
            stripped = line.strip()
            if not stripped or ':' not in stripped:
                continue
            label, _, raw_value = stripped.partition(':')
            key = alias_map.get(_normalise_label(label))
            if key is None:
                if not stripped.startswith(('OCR_QUALITY:', 'UNREADABLE_GLYPHS:', 'CAPTURE_ORIENTATION:', 'SECURITY NOTE:')):
                    warnings.append(f'UNPARSED_LINE:{stripped[:40]}')
                continue
            value = raw_value.strip()
            fields[key] = FieldValue(raw=value, value=value, confidence=1.0)
        for field_name in mandatory:
            if field_name not in fields:
                fields[field_name] = FieldValue(raw=None, value=None, confidence=1.0)
        missing_fields = [
            field_name
            for field_name in mandatory
            if field_name in fields and fields[field_name].value is None
        ]
        if 'OCR_QUALITY: DEGRADED' in raw_text:
            warnings.append('DEGRADED_OCR_QUALITY')
        if 'CAPTURE_ORIENTATION: 90_DEGREES' in raw_text:
            warnings.append('ROTATED_CAPTURE')
        return ExtractionResult(
            document_id=document_id,
            fields=fields,
            missing_fields=missing_fields,
            warnings=warnings,
            raw_text=raw_text,
            adapter_name=self.adapter_name,
            adapter_version=self.adapter_version,
        )


def extract_text(document_id: str) -> str:
    return load_sidecar(document_id)
