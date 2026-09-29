from src.adapters.sidecar_text import SidecarAdapter
from src.repository import list_cases, load_ground_truth
from src.validation.doctype import normalise


def test_TST_13_011_doctype_normalisation_matches_ground_truth():
    adapter = SidecarAdapter()
    checked = 0
    for case in list_cases():
        for document_id in case['document_ids']:
            raw_type = adapter.extract(document_id).fields['document_type'].raw
            assert normalise(raw_type) == load_ground_truth(document_id)['document_type']
            checked += 1
    assert checked == 13
