from __future__ import annotations

from datetime import date
import re
from typing import Any

from src.validation.doctype import normalise


def completeness(fields: dict[str, Any], policy: dict[str, Any]) -> float:
    required = tuple(policy.get('mandatory_fields', ()))
    if not required:
        return 0.0
    return round(sum(bool(fields.get(name)) for name in required) / len(required), 3)


def validate(
    fields: dict[str, Any],
    policy: dict[str, Any],
    decision_date: date,
    tamper_signals: list[str],
    raw_text: str = '',
) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    warnings: list[str] = []
    document_type = normalise(fields.get('document_type'))
    supported_types = {normalise(value) for value in policy.get('supported_types', [])}
    unsupported_type = document_type is None or document_type not in supported_types
    if unsupported_type:
        reasons.append('UNSUPPORTED_DOCUMENT_TYPE')

    missing_fields = [
        name for name in policy.get('mandatory_fields', [])
        if not fields.get(name)
    ]
    for name in missing_fields:
        reasons.append(f'MISSING_MANDATORY_FIELD_{name.upper()}')

    score = completeness(fields, policy)
    threshold = float(policy.get('completeness_threshold', 0.75))
    if missing_fields or score < threshold:
        reasons.append('INSUFFICIENT_MANDATORY_FIELDS')

    number = fields.get('document_number')
    pattern = policy.get('number_patterns', {}).get(document_type or '')
    if pattern and number and not re.fullmatch(pattern, str(number)):
        reasons.append('INVALID_DOCUMENT_NUMBER_FORMAT')

    expiry = fields.get('expiry_date')
    if expiry:
        try:
            if date.fromisoformat(str(expiry)) < decision_date:
                reasons.append('DOCUMENT_EXPIRED')
        except ValueError:
            reasons.append('INVALID_EXPIRY_DATE')

    for signal in tamper_signals:
        if signal not in reasons:
            reasons.append(signal)

    if 'DEGRADED' in raw_text:
        warnings.append('OCR_QUALITY_DEGRADED')
    if '90_DEGREES' in raw_text:
        warnings.append('ROTATED_DOCUMENT')

    if any(reason in reasons for reason in ('DOCUMENT_EXPIRED', 'SUSPECTED_TAMPERING')):
        decision = 'REJECT'
    elif reasons or warnings:
        decision = 'REVIEW'
        if unsupported_type and 'MANUAL_REVIEW_REQUIRED' not in reasons:
            reasons.append('MANUAL_REVIEW_REQUIRED')
        elif not reasons:
            reasons.append('MANUAL_REVIEW_REQUIRED')
    else:
        decision = 'APPROVE'
        reasons.append('BASELINE_RULES_PASSED')

    if decision in {'REVIEW', 'REJECT'}:
        reasons = [reason for reason in reasons if reason != 'BASELINE_RULES_PASSED']
    return decision, reasons, warnings