from datetime import date
from pathlib import Path
import subprocess
import sys

from src import adapters
from src.adapters.clocks import FixedClock
from src.adapters.tamper_marker import MarkerSignal
from src.orchestrator import wiring
from src.service import verify_document

ROOT = Path(__file__).resolve().parents[2]


def _passport_text(*, number='PXT123456', expiry='2035-01-01', include_name=True):
    lines = ['DOCUMENT TYPE: PASSPORT']
    if include_name:
        lines.append('NAME: Ari Example')
    lines.extend([
        'DOB: 1990-01-01',
        f'DOCUMENT NO: {number}',
        f'EXPIRY DATE: {expiry}',
    ])
    return '\n'.join(lines) + '\n'


def _patch_sidecar(monkeypatch, text):
    monkeypatch.setattr(adapters.sidecar_text, 'load_sidecar', lambda _document_id: text)
    provider = wiring.get_extraction_provider()
    monkeypatch.setattr('src.service.get_extraction_provider', lambda: provider)


def test_TST_13_013_expired_with_fixed_clock():
    original_clock = wiring.get_clock()
    wiring.set_clock(FixedClock(date(2026, 9, 9)))
    try:
        result = verify_document('CASE-004-PASSPORT')
        assert result.decision == 'REJECT'
        assert 'DOCUMENT_EXPIRED' in result.reason_codes
    finally:
        wiring.set_clock(original_clock)


def test_TST_13_015_decision_date_from_clock(monkeypatch):
    original_clock = wiring.get_clock()
    wiring.set_clock(FixedClock(date(2031, 1, 1)))
    try:
        sample = verify_document('CASE-001-PASSPORT')
        assert sample.decision != 'REJECT'
        assert 'DOCUMENT_EXPIRED' not in sample.reason_codes

        _patch_sidecar(monkeypatch, _passport_text(expiry='2030-12-31'))
        fixture = verify_document('CASE-001-PASSPORT')
        assert fixture.decision == 'REJECT'
        assert 'DOCUMENT_EXPIRED' in fixture.reason_codes
    finally:
        wiring.set_clock(original_clock)

    source_root = ROOT / 'src'
    assert all('2026-09-09' not in path.read_text(encoding='utf-8') for path in source_root.rglob('*.py'))


def test_TST_13_016_invalid_expiry_reviews(monkeypatch):
    _patch_sidecar(monkeypatch, _passport_text(expiry='2030-13-45'))
    result = verify_document('CASE-001-PASSPORT')
    assert result.decision == 'REVIEW'
    assert 'INVALID_EXPIRY_DATE' in result.reason_codes


def test_TST_13_017_missing_name_reviews(monkeypatch):
    _patch_sidecar(monkeypatch, _passport_text(include_name=False))
    result = verify_document('CASE-001-PASSPORT')
    assert result.decision == 'REVIEW'
    assert 'full_name' not in result.parsed_fields
    assert 'full_name' in result.missing_fields
    assert 'INSUFFICIENT_MANDATORY_FIELDS' in result.reason_codes
    assert 'MISSING_MANDATORY_FIELD_FULL_NAME' in result.reason_codes


def test_TST_13_018_malformed_number_reviews(monkeypatch):
    _patch_sidecar(monkeypatch, _passport_text(number='PX123'))
    result = verify_document('CASE-001-PASSPORT')
    assert result.decision == 'REVIEW'
    assert 'INVALID_DOCUMENT_NUMBER_FORMAT' in result.reason_codes


def test_bs03_tamper_via_provider(monkeypatch):
    class StubTamperProvider:
        def signals(self, extraction):
            return ['SUSPECTED_TAMPERING']

    monkeypatch.setattr(wiring, '_default_tamper_provider', StubTamperProvider())
    clean = verify_document('CASE-001-PASSPORT')
    assert clean.decision == 'REJECT'
    assert 'SUSPECTED_TAMPERING' in clean.reason_codes

    marker = MarkerSignal()
    provider = wiring.get_extraction_provider()
    assert marker.signals(provider.extract('CASE-006-PASSPORT')) == ['SUSPECTED_TAMPERING']
    assert marker.signals(provider.extract('CASE-001-PASSPORT')) == []


def test_bs03_validation_layer_is_pure():
    code = '''
import sys
from datetime import date
from src.validation.rules import validate
policy = {
    "supported_types": ["passport"],
    "mandatory_fields": ["full_name", "date_of_birth", "document_number", "expiry_date"],
    "completeness_threshold": 0.75,
    "number_patterns": {"passport": r"^PXT\\d{6}$"},
}
fields = {
    "document_type": "PASSPORT",
    "full_name": "Ari Example",
    "date_of_birth": "1990-01-01",
    "document_number": "PXT123456",
    "expiry_date": "2035-01-01",
}
assert validate(fields, policy, date(2030, 1, 1), [], "")[0] == "APPROVE"
forbidden = ("src.orchestrator", "src.adapters")
assert not [name for name in sys.modules if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden)]
'''
    result = subprocess.run(
        [sys.executable, '-c', code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
