import json
from pathlib import Path

import pytest

from src.adapters.file_policy_source import FilePolicySource, PolicyLoadError


ROOT = Path(__file__).resolve().parents[1]


def test_TST_13_064_unlisted_approver_rejected(tmp_path):
    policy = json.loads((ROOT.parent / 'config' / 'policy_v1.json').read_text(encoding='utf-8'))
    policy['approved_by'] = 'Unknown approver'
    path = tmp_path / 'bad_policy.json'
    path.write_text(json.dumps(policy), encoding='utf-8')
    with pytest.raises(PolicyLoadError):
        FilePolicySource(path)
