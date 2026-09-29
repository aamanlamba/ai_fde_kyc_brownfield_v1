from src import adapters
from src.adapters.sidecar_text import SidecarAdapter
from src.service import verify_document


def test_TST_13_009_unparsed_line_reaches_rules(monkeypatch):
    text = 'DOCUMENT TYPE: PASSPORT\nNAME: Ari Example\nDOB: 1990-01-01\nDOCUMENT NO: PXT123456\nEXPIRY DATE: 2035-01-01\nFOO BAR: x\n'
    monkeypatch.setattr(adapters.sidecar_text, 'load_sidecar', lambda _document_id: text)
    provider = SidecarAdapter()
    monkeypatch.setattr('src.service.get_extraction_provider', lambda: provider)
    result = verify_document('CASE-001-PASSPORT')
    assert result.decision == 'REVIEW'
    assert 'UNREAD_EVIDENCE' in result.reason_codes
