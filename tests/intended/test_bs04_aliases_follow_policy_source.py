from src import adapters, rules
from src.adapters.sidecar_text import SidecarAdapter


def test_bs04_aliases_follow_policy_source(monkeypatch):
    policy = dict(rules.get_policy_source().get_policy())
    policy['label_aliases'] = dict(policy['label_aliases'])
    policy['label_aliases']['NAME'] = ['CLIENT IDENTIFIER']

    class Policy:
        def get_policy(self):
            return policy

    text = 'DOCUMENT TYPE: PASSPORT\nCLIENT IDENTIFIER: Ari Example\nDOB: 1990-01-01\nDOCUMENT NO: PXT123456\nEXPIRY DATE: 2035-01-01\n'
    monkeypatch.setattr(adapters.sidecar_text, 'load_sidecar', lambda _document_id: text)
    original = rules.get_policy_source()
    rules.set_policy_source(Policy())
    try:
        result = SidecarAdapter().extract('CASE-001-PASSPORT')
        assert result.fields['full_name'].value == 'Ari Example'
    finally:
        rules.set_policy_source(original)