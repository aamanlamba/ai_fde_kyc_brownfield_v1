from src.repository import list_cases
from src.validation.doctype import normalise


def test_TST_13_011_doctype_normalisation_matches_ground_truth():
    docs = []
    for case in list_cases():
        for document_id in case['document_ids']:
            docs.append(document_id)
    assert docs
    assert normalise('PASSPORT') == 'passport'
    assert normalise('NATIONAL_ID') == 'national_id'
    assert normalise('DRIVING LICENCE') == 'driving_licence'
