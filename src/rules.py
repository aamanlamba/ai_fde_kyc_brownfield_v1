from __future__ import annotations

import re
from datetime import date
from typing import Any

from src.orchestrator.wiring import (
    get_clock,
    get_policy,
    get_policy_source as _get_policy_source,
    get_tamper_provider,
    set_policy_source as _set_policy_source,
)
from src.ports import Clock, ExtractionResult, FieldValue
from src.validation.rules import completeness as _completeness
from src.validation.rules import validate

MANDATORY: tuple[str, ...] = tuple()
PATTERNS: dict[str, re.Pattern[str] | str] = {}
COMPLETENESS_THRESHOLD = 0.75


def _current_policy() -> dict[str, Any]:
    return get_policy()


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
    return _get_policy_source()


def set_policy_source(source):
    _set_policy_source(source)
    _sync_runtime_policy()


def completeness(fields: dict) -> float:
    return _completeness(fields, _current_policy())


def evaluate(fields: dict, raw_text: str, clock: Clock | None = None) -> tuple[str, list[str], list[str]]:
    policy = _current_policy()
    extraction = ExtractionResult(
        document_id='rules-shim',
        fields={
            name: value if isinstance(value, FieldValue) else FieldValue(raw=value, value=value)
            for name, value in fields.items()
        },
        raw_text=raw_text,
    )
    signals = get_tamper_provider().signals(extraction)
    return validate(fields, policy, (clock or get_clock()).today(), signals, raw_text)

