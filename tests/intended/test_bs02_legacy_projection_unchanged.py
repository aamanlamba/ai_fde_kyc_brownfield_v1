import json
from pathlib import Path

from src.repository import list_cases
from src.service import verify_case

ROOT = Path(__file__).resolve().parents[2]


def _matches_legacy_projection(expected, actual):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _matches_legacy_projection(value, actual[key])
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        return isinstance(actual, list) and len(expected) == len(actual) and all(
            _matches_legacy_projection(expected_item, actual_item)
            for expected_item, actual_item in zip(expected, actual)
        )
    return expected == actual


def test_bs02_legacy_projection_unchanged():
    intended_changes = json.loads((ROOT / 'config' / 'intended_changes.json').read_text(encoding='utf-8'))
    for case in list_cases():
        case_id = case['case_id']
        expected_path = ROOT / 'data' / 'expected_baseline_outputs' / f'{case_id}.json'
        expected = json.loads(expected_path.read_text(encoding='utf-8'))
        actual = verify_case(case_id).model_dump(mode='json')
        ignored_case_keys = set(intended_changes.get(case_id, {}).get('keys', []))
        expected_projection = {key: value for key, value in expected.items() if key not in ignored_case_keys}
        actual_projection = {key: value for key, value in actual.items() if key not in ignored_case_keys}
        assert _matches_legacy_projection(expected_projection, actual_projection)
