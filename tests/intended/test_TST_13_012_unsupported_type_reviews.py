from src import adapters
from src.service import verify_document


def test_TST_13_012_unsupported_type_reviews(monkeypatch):
    text = 'DOCUMENT TYPE: RESIDENCE_PERMIT\nNAME: Ari Example\nDOB: 1990-01-01\nDOCUMENT NO: RP123456\nEXPIRY DATE: 2035-01-01\n'
    monkeypatch.setattr(adapters.sidecar_text, 'load_sidecar', lambda _document_id: text)
    result = verify_document('CASE-001-PASSPORT')
    assert result.decision == 'REVIEW'
    assert 'UNSUPPORTED_DOCUMENT_TYPE' in result.reason_codes
    assert result.decision != 'APPROVE'
