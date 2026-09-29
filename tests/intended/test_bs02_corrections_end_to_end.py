from src.adapters import sidecar_text
from src.adapters.sidecar_text import SidecarAdapter
from src.service import verify_document


def _verify_sidecar(monkeypatch, text, document_id='CASE-001-PASSPORT'):
    monkeypatch.setattr(sidecar_text, 'load_sidecar', lambda _document_id: text)
    monkeypatch.setattr('src.service.get_extraction_provider', lambda: SidecarAdapter())
    return verify_document(document_id)


def _complete_text(document_type, name_label, dob_label):
    return (
        f'DOCUMENT TYPE: {document_type}\n'
        f'{name_label}: Ari Example\n'
        f'{dob_label}: 1990-01-01\n'
        'DOCUMENT NO: PXT123456\n'
        'EXPIRY DATE: 2035-01-01\n'
    )


def test_bs02_alias_labels_end_to_end(monkeypatch):
    fixtures = (
        _complete_text('PASSPORT', 'Name ', 'DATE OF BIRTH'),
        _complete_text('passport', 'name', 'DOB'),
        _complete_text('PASSPORT', 'NAME', 'date of birth'),
    )
    for text in fixtures:
        result = _verify_sidecar(monkeypatch, text)
        assert result.decision == 'APPROVE'
        assert result.reason_codes == ['BASELINE_RULES_PASSED']


def test_bs02_unsupported_type_keeps_tamper(monkeypatch):
    text = _complete_text('RESIDENCE_PERMIT', 'NAME', 'DOB') + 'SECURITY NOTE: ALTERED_TEXT_REGION_DETECTED\n'
    result = _verify_sidecar(monkeypatch, text)
    assert result.decision == 'REJECT'
    assert 'SUSPECTED_TAMPERING' in result.reason_codes
    assert 'UNSUPPORTED_DOCUMENT_TYPE' in result.reason_codes


def test_bs02_no_passed_code_on_review(monkeypatch):
    from src.repository import list_cases
    from src.service import verify_case

    results = []
    for case in list_cases():
        results.extend(verify_case(case['case_id']).documents)
    alias_fixtures = (
        _complete_text('PASSPORT', 'Name ', 'DATE OF BIRTH'),
        _complete_text('passport', 'name', 'DOB'),
        _complete_text('PASSPORT', 'NAME', 'date of birth'),
    )
    results.extend(_verify_sidecar(monkeypatch, text) for text in alias_fixtures)
    tampered = _complete_text('RESIDENCE_PERMIT', 'NAME', 'DOB') + 'SECURITY NOTE: ALTERED_TEXT_REGION_DETECTED\n'
    results.append(_verify_sidecar(monkeypatch, tampered))
    assert all(
        result.decision == 'APPROVE' or 'BASELINE_RULES_PASSED' not in result.reason_codes
        for result in results
    )