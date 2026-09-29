from src.adapters.file_policy_source import FilePolicySource


def test_bs02_policy_loaded_once():
    source = FilePolicySource()
    first = source.get_policy()
    second = source.get_policy()
    assert first == second
    assert first['policy_version'] == '1.1.0'
