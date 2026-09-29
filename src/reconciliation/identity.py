from __future__ import annotations

import re
import unicodedata
from typing import TypedDict


class ReconciliationResult(TypedDict):
    attribute: str
    subject_a: str
    subject_b: str
    result: str
    reason: str | None


def _normalise_name(value: str) -> str:
    folded = value.casefold()
    without_punctuation = ''.join(
        character for character in folded
        if not unicodedata.category(character).startswith('P')
    )
    collapsed = re.sub(r'\s+', ' ', without_punctuation).strip()
    decomposed = unicodedata.normalize('NFKD', collapsed)
    return ''.join(
        character for character in decomposed
        if not unicodedata.category(character).startswith('M')
    )


def _apply_ocr_confusions(value: str, confusions: list[list[str]]) -> str:
    transformed = value
    for pair in confusions:
        if len(pair) == 2:
            source, replacement = pair
            transformed = transformed.replace(source.casefold(), replacement.casefold())
    return transformed


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + (left_char != right_char),
            ))
        previous = current
    return previous[-1]


def _initial_match(left: list[str], right: list[str]) -> bool:
    if len(left) != len(right):
        return False

    assigned_left = [-1] * len(right)

    def assign(left_index: int, seen: set[int]) -> bool:
        for candidate, second in enumerate(right):
            if candidate in seen:
                continue
            first = left[left_index]
            matches = first == second or (
                (len(first) == 1 and second.startswith(first))
                or (len(second) == 1 and first.startswith(second))
            )
            if matches:
                seen.add(candidate)
                if assigned_left[candidate] == -1 or assign(assigned_left[candidate], seen):
                    assigned_left[candidate] = left_index
                    return True
        return False

    return all(assign(index, set()) for index in range(len(left)))


def _classify_name(left_value: str | None, right_value: str | None, policy: dict) -> str:
    if not left_value or not right_value:
        return 'MISMATCH'
    left = _normalise_name(left_value)
    right = _normalise_name(right_value)
    if left == right:
        return 'EXACT'

    confusions = policy.get('ocr_confusions', [])
    left_ocr = _apply_ocr_confusions(left, confusions)
    right_ocr = _apply_ocr_confusions(right, confusions)
    if left_ocr == right_ocr:
        return 'MATCH_AFTER_OCR_NORMALISATION'

    left_tokens = left_ocr.split()
    right_tokens = right_ocr.split()
    if sorted(left_tokens) == sorted(right_tokens) or _initial_match(left_tokens, right_tokens):
        return 'TOLERATED'

    maximum = policy.get('name_variation_max', 1)
    if len(left_tokens) == len(right_tokens) and all(
        first == second or _levenshtein(first, second) <= maximum
        for first, second in zip(left_tokens, right_tokens)
    ):
        return 'VARIATION'
    return 'MISMATCH'


def _name_reason(result: str) -> str | None:
    if result == 'VARIATION':
        return 'IDENTITY_NAME_VARIATION'
    if result == 'MISMATCH':
        return 'IDENTITY_NAME_MISMATCH'
    return None


def _normalise_address(value: str) -> str:
    return _normalise_name(value)


def reconcile(
    application: dict,
    documents: list[dict],
    policy: dict,
) -> list[ReconciliationResult]:
    results: list[ReconciliationResult] = []
    application_name = application.get('submitted_name')
    application_dob = application.get('submitted_dob')
    application_address = application.get('submitted_address')

    def add_name(left_subject: str, left_name: str | None, right_subject: str, right_name: str | None) -> None:
        outcome = _classify_name(left_name, right_name, policy)
        results.append({
            'attribute': 'full_name',
            'subject_a': left_subject,
            'subject_b': right_subject,
            'result': outcome,
            'reason': _name_reason(outcome),
        })

    def add_dob(left_subject: str, left_dob: str | None, right_subject: str, right_dob: str | None) -> None:
        if not left_dob or not right_dob:
            return
        differs = left_dob != right_dob
        results.append({
            'attribute': 'date_of_birth',
            'subject_a': left_subject,
            'subject_b': right_subject,
            'result': 'MISMATCH' if differs else 'EXACT',
            'reason': 'IDENTITY_DOB_MISMATCH' if differs else None,
        })

    def add_address(left_subject: str, left_address: str | None, right_subject: str, right_address: str | None) -> None:
        if left_address and right_address and _normalise_address(left_address) != _normalise_address(right_address):
            results.append({
                'attribute': 'address',
                'subject_a': left_subject,
                'subject_b': right_subject,
                'result': 'ADDRESS_DIFFERS',
                'reason': None,
            })

    for document in documents:
        fields = document.get('fields', {})
        document_id = document['document_id']
        add_name(document_id, fields.get('full_name'), 'application', application_name)
        add_dob(document_id, fields.get('date_of_birth'), 'application', application_dob)
        add_address(document_id, fields.get('address'), 'application', application_address)

    for index, document_a in enumerate(documents):
        fields_a = document_a.get('fields', {})
        for document_b in documents[index + 1:]:
            fields_b = document_b.get('fields', {})
            subject_a = document_a['document_id']
            subject_b = document_b['document_id']
            add_name(subject_a, fields_a.get('full_name'), subject_b, fields_b.get('full_name'))
            add_dob(subject_a, fields_a.get('date_of_birth'), subject_b, fields_b.get('date_of_birth'))
            add_address(subject_a, fields_a.get('address'), subject_b, fields_b.get('address'))

    return results