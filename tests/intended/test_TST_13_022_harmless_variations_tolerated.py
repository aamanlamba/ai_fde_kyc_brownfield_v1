from pathlib import Path
import subprocess
import sys

from src.reconciliation.identity import reconcile

ROOT = Path(__file__).resolve().parents[2]
POLICY = {
    'name_variation_max': 1,
    'ocr_confusions': [['rn', 'm'], ['0', 'o'], ['1', 'l'], ['5', 's']],
}


def _reconcile_names(name_a, name_b):
    return reconcile(
        {'submitted_name': name_a, 'submitted_dob': '1990-01-01'},
        [{'document_id': 'DOC-A', 'fields': {'full_name': name_b, 'date_of_birth': '1990-01-01'}}],
        POLICY,
    )


def test_TST_13_022_harmless_variations_tolerated():
    pairs = (
        ('ALICE SMITH', 'alice smith'),
        ('Alice   Smith', 'Alice Smith'),
        ("O'Brien Smith", 'OBrien Smith'),
        ('Jose Garcia', 'José García'),
        ('Smith Alice', 'Alice Smith'),
        ('J Smith', 'John Smith'),
    )
    for application_name, document_name in pairs:
        result = _reconcile_names(application_name, document_name)
        assert result[0]['result'] in {'EXACT', 'TOLERATED'}
        assert result[0]['reason'] is None

    address_results = reconcile(
        {
            'submitted_name': 'Alice Smith',
            'submitted_dob': '1990-01-01',
            'submitted_address': '10 Main Street',
        },
        [{
            'document_id': 'DOC-A',
            'fields': {
                'full_name': 'Alice Smith',
                'date_of_birth': '1990-01-01',
                'address': '20 Main Street',
            },
        }],
        POLICY,
    )
    address_result = next(item for item in address_results if item['attribute'] == 'address')
    assert address_result['result'] == 'ADDRESS_DIFFERS'
    assert address_result['reason'] is None

    script = '''
import sys
from src.reconciliation.identity import reconcile
app = {"submitted_name": "Alice Smith", "submitted_dob": "1990-01-01"}
docs = [{"document_id": "DOC", "fields": {"full_name": "Smith Alice", "date_of_birth": "1990-01-01"}}]
assert reconcile(app, docs, {"name_variation_max": 1, "ocr_confusions": []})[0]["result"] == "TOLERATED"
forbidden = ("src.adapters", "src.orchestrator")
assert not [name for name in sys.modules if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden)]
'''
    subprocess_result = subprocess.run(
        [sys.executable, '-c', script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert subprocess_result.returncode == 0, subprocess_result.stderr