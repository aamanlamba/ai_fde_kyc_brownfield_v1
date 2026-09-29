from pathlib import Path

from src.adapters.sidecar_text import SidecarAdapter
from src.repository import load_sidecar

ROOT = Path(__file__).resolve().parents[1]


def test_TST_13_006_sidecar_extraction_matches_baseline():
    adapter = SidecarAdapter()
    for doc_id in sorted({p.stem for p in (ROOT.parent / 'data' / 'sidecar_ocr').glob('*.txt')}):
        extraction = adapter.extract(doc_id)
        assert extraction.raw_text == load_sidecar(doc_id)
        assert extraction.document_id == doc_id
        assert extraction.adapter_name == 'SidecarAdapter'
        assert 'Moharnmad' not in extraction.raw_text or 'Moharnmad Rehrnan' in extraction.raw_text
