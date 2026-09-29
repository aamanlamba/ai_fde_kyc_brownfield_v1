import socket

from src.adapters.mock_extraction import MockAdapter
from src.ports import ExtractionUnavailable
from src.service import verify_document


def test_TST_13_010_extraction_unavailable_reviews_offline(monkeypatch):
    adapter = MockAdapter(exc=ExtractionUnavailable('CASE-001-PASSPORT'))
    monkeypatch.setattr('src.service.get_extraction_provider', lambda: adapter)

    def reject_socket(*args, **kwargs):
        raise AssertionError('network access is forbidden in this test')

    monkeypatch.setattr(socket, 'socket', reject_socket)
    result = verify_document('CASE-001-PASSPORT')
    assert result.decision == 'REVIEW'
    assert result.reason_codes == ['EXTRACTION_UNAVAILABLE']
    assert result.parsed_fields == {}
