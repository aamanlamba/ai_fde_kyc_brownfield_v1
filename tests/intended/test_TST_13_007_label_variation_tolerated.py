from src import adapters
from src.adapters.sidecar_text import SidecarAdapter


def test_TST_13_007_label_variation_tolerated(monkeypatch):
    text = "DOCUMENT TYPE: PASSPORT\nNAME : Aarav Mehta\nDATE OF BIRTH: 1991-04-12\nDOCUMENT NUMBER: PXT100184\nEXPIRY DATE: 2033-05-31\n"
    monkeypatch.setattr(adapters.sidecar_text, 'load_sidecar', lambda _document_id: text)
    adapter = SidecarAdapter()
    result = adapter.extract('CASE-001-PASSPORT')
    assert result.fields['full_name'].value == 'Aarav Mehta'
    assert result.fields['date_of_birth'].value == '1991-04-12'
    assert result.fields['document_number'].value == 'PXT100184'
