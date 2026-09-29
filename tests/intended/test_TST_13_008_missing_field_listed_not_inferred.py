from src import adapters
from src.adapters.sidecar_text import SidecarAdapter


def test_TST_13_008_missing_field_listed_not_inferred(monkeypatch):
    text = "DOCUMENT TYPE: PASSPORT\nDOB: 1991-04-12\nDOCUMENT NO: PXT100184\nEXPIRY DATE: 2033-05-31\n"
    monkeypatch.setattr(adapters.sidecar_text, 'load_sidecar', lambda _document_id: text)
    adapter = SidecarAdapter()
    result = adapter.extract('CASE-001-PASSPORT')
    assert 'full_name' in result.fields
    assert result.fields['full_name'].value is None
    assert 'full_name' in result.missing_fields
