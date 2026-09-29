import json
from pathlib import Path

import pytest

from src.adapters.file_policy_source import FilePolicySource, PolicyLoadError


ROOT = Path(__file__).resolve().parents[1]


def test_TST_13_033_invalid_policy_rejected(tmp_path):
    valid = json.loads((ROOT.parent / 'config' / 'policy_v1.json').read_text(encoding='utf-8'))

    missing_key = valid.copy()
    missing_key.pop('approved_by')
    missing_key_path = tmp_path / 'missing_key.json'
    missing_key_path.write_text(json.dumps(missing_key), encoding='utf-8')
    with pytest.raises(PolicyLoadError):
        FilePolicySource(missing_key_path)

    missing_approved = valid.copy()
    missing_approved['approved_by'] = ''
    missing_approved_path = tmp_path / 'missing_approved.json'
    missing_approved_path.write_text(json.dumps(missing_approved), encoding='utf-8')
    with pytest.raises(PolicyLoadError):
        FilePolicySource(missing_approved_path)

    missing_patterns = valid.copy()
    missing_patterns.pop('number_patterns')
    missing_patterns_path = tmp_path / 'missing_patterns.json'
    missing_patterns_path.write_text(json.dumps(missing_patterns), encoding='utf-8')
    with pytest.raises(PolicyLoadError):
        FilePolicySource(missing_patterns_path)

    invalid_variation = valid.copy()
    invalid_variation['name_variation_max'] = True
    invalid_variation_path = tmp_path / 'invalid_variation.json'
    invalid_variation_path.write_text(json.dumps(invalid_variation), encoding='utf-8')
    with pytest.raises(PolicyLoadError):
        FilePolicySource(invalid_variation_path)

    invalid_confusions = valid.copy()
    invalid_confusions['ocr_confusions'] = [['rn']]
    invalid_confusions_path = tmp_path / 'invalid_confusions.json'
    invalid_confusions_path.write_text(json.dumps(invalid_confusions), encoding='utf-8')
    with pytest.raises(PolicyLoadError):
        FilePolicySource(invalid_confusions_path)
