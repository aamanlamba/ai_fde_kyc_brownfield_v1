from pathlib import Path
import json

from src.adapters.sidecar_text import SidecarAdapter
from src.repository import list_cases, load_sidecar

ROOT = Path(__file__).resolve().parents[1]


def test_TST_13_006_sidecar_extraction_matches_baseline():
    adapter = SidecarAdapter()
    baselines = {}
    for case in list_cases():
        path = ROOT.parent / 'data' / 'expected_baseline_outputs' / f"{case['case_id']}.json"
        output = json.loads(path.read_text(encoding='utf-8'))
        baselines.update({document['document_id']: document['parsed_fields'] for document in output['documents']})
    for doc_id in sorted(baselines):
        extraction = adapter.extract(doc_id)
        assert extraction.raw_text == load_sidecar(doc_id)
        assert extraction.document_id == doc_id
        assert extraction.adapter_name == 'SidecarAdapter'
        for name, extracted in extraction.fields.items():
            if extracted.value is not None:
                assert baselines[doc_id][name] == extracted.value
    assert adapter.extract('CASE-005-NID').fields['full_name'].raw == 'Moharnmad Rehrnan'
