from src import adapters
from src.service import verify_case


def _fixture_case(monkeypatch, application_name, application_dob, document_name, document_dob):
    import src.service as service

    application = {
        'case_id': 'FIXTURE-CASE',
        'submitted_name': application_name,
        'submitted_dob': application_dob,
        'submitted_address': '10 Main Street',
        'document_ids': ['FIXTURE-DOC'],
    }
    text = (
        'DOCUMENT TYPE: PASSPORT\n'
        f'NAME: {document_name}\n'
        f'DOB: {document_dob}\n'
        'DOCUMENT NO: PXT123456\n'
        'EXPIRY DATE: 2035-01-01\n'
    )
    monkeypatch.setattr(service, 'load_application', lambda _case_id: application)
    monkeypatch.setattr(adapters.sidecar_text, 'load_sidecar', lambda _document_id: text)
    return service.verify_case('FIXTURE-CASE')


def test_TST_13_019_case005_name_variation_reviews():
    result = verify_case('CASE-005')
    assert result.decision == 'REVIEW'
    assert result.reason_codes == ['IDENTITY_NAME_VARIATION', 'MANUAL_REVIEW_REQUIRED']
    assert any(
        entry['attribute'] == 'full_name'
        and entry['subject_a'] == 'CASE-005-PASSPORT'
        and entry['subject_b'] == 'application'
        and entry['result'] == 'VARIATION'
        for entry in result.reconciliation
    )
    assert any(
        entry['attribute'] == 'full_name'
        and entry['subject_a'] == 'CASE-005-PASSPORT'
        and entry['subject_b'] == 'CASE-005-NID'
        and entry['result'] == 'VARIATION'
        for entry in result.reconciliation
    )


def test_TST_13_020_ocr_confusion_tolerated():
    result = verify_case('CASE-005')
    entry = next(
        item for item in result.reconciliation
        if item['attribute'] == 'full_name'
        and item['subject_a'] == 'CASE-005-NID'
        and item['subject_b'] == 'application'
    )
    assert entry['result'] == 'MATCH_AFTER_OCR_NORMALISATION'
    assert result.documents[1].parsed_fields['full_name'] == 'Moharnmad Rehrnan'


def test_TST_13_021_clean_cases_no_identity_reason():
    from pathlib import Path
    import json

    root = Path(__file__).resolve().parents[2]
    for case_id in ('CASE-001', 'CASE-002', 'CASE-003', 'CASE-004', 'CASE-006'):
        baseline = json.loads((root / 'data' / 'expected_baseline_outputs' / f'{case_id}.json').read_text(encoding='utf-8'))
        result = verify_case(case_id)
        assert result.decision == baseline['decision']
        assert result.reason_codes == baseline['reason_codes']
        assert not any(reason.startswith('IDENTITY_') for reason in result.reason_codes)


def test_TST_13_023_dob_mismatch_reviews(monkeypatch):
    result = _fixture_case(monkeypatch, 'Ari Example', '1990-01-01', 'Ari Example', '1990-01-02')
    assert result.decision == 'REVIEW'
    assert 'IDENTITY_DOB_MISMATCH' in result.reason_codes


def test_TST_13_024_unrelated_name_mismatch(monkeypatch):
    result = _fixture_case(monkeypatch, 'Ari Example', '1990-01-01', 'Taylor Morgan', '1990-01-01')
    assert result.decision == 'REVIEW'
    assert 'IDENTITY_NAME_MISMATCH' in result.reason_codes