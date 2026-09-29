from __future__ import annotations

from datetime import date
import re
from typing import Any

from src.adapters.clocks import SystemClock
from src.adapters.file_policy_source import DEFAULT_POLICY_PATH, FilePolicySource
from src.ports import Clock

_policy_source = FilePolicySource(DEFAULT_POLICY_PATH)
REFERENCE_DATE = SystemClock().today()
MANDATORY: tuple[str, ...] = tuple()
PATTERNS: dict[str, re.Pattern[str] | str] = {}
COMPLETENESS_THRESHOLD = 0.75


def _current_policy() -> dict[str, Any]:
    if hasattr(_policy_source, 'load_policy'):
        return _policy_source.load_policy()
    if callable(_policy_source):
        return _policy_source()
    return dict(_policy_source)


def _sync_runtime_policy() -> None:
    global MANDATORY, PATTERNS, COMPLETENESS_THRESHOLD
    policy = _current_policy()
    MANDATORY = tuple(policy.get('mandatory_fields', ('full_name', 'date_of_birth', 'document_number', 'expiry_date')))
    PATTERNS = {
        key: (re.compile(value) if isinstance(value, str) else value)
        for key, value in policy.get('number_patterns', {}).items()
    }
    COMPLETENESS_THRESHOLD = float(policy.get('completeness_threshold', 0.75))


_sync_runtime_policy()


def get_policy_source():
    return _policy_source


def set_policy_source(source):
    global _policy_source
    _policy_source = source
    _sync_runtime_policy()


def completeness(fields: dict) -> float:
    required = tuple(_current_policy().get('mandatory_fields', MANDATORY) or MANDATORY)
    if not required:
        return 0.0
    return round(sum(bool(fields.get(k)) for k in required) / len(required), 3)


def evaluate(fields: dict, raw_text: str, clock: Clock | None = None) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    warnings: list[str] = []
    policy = _current_policy()
    dtype = fields.get('document_type', '').lower()
    c = completeness(fields)
    threshold = float(policy.get('completeness_threshold', COMPLETENESS_THRESHOLD))
    if c < threshold:
        reasons.append('INSUFFICIENT_MANDATORY_FIELDS')
    num = fields.get('document_number', '')
    pat = policy.get('number_patterns', PATTERNS).get(dtype) or PATTERNS.get(dtype)
    if pat and num and not re.fullmatch(pat, num):
        reasons.append('INVALID_DOCUMENT_NUMBER_FORMAT')
    expiry = fields.get('expiry_date')
    if expiry:
        try:
            decision_date = (clock or SystemClock()).today()
            if date.fromisoformat(expiry) < decision_date:
                reasons.append('DOCUMENT_EXPIRED')
        except ValueError:
            reasons.append('INVALID_EXPIRY_DATE')
    if 'ALTERED_TEXT_REGION_DETECTED' in raw_text:
        reasons.append('SUSPECTED_TAMPERING')
    if 'DEGRADED' in raw_text:
        warnings.append('OCR_QUALITY_DEGRADED')
    if '90_DEGREES' in raw_text:
        warnings.append('ROTATED_DOCUMENT')
    if any(r in reasons for r in ('SUSPECTED_TAMPERING', 'DOCUMENT_EXPIRED')):
        return 'REJECT', reasons, warnings
    if reasons or warnings:
        return 'REVIEW', reasons or ['MANUAL_REVIEW_REQUIRED'], warnings
    return 'APPROVE', ['BASELINE_RULES_PASSED'], warnings

