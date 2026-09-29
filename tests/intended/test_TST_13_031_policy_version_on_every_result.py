from src.adapters.file_policy_source import FilePolicySource
from src.service import verify_case


def test_TST_13_031_policy_version_on_every_result():
    policy = FilePolicySource().get_policy()
    case = verify_case('CASE-001')
    assert case.policy_version == policy['policy_version']
    for document in case.documents:
        assert document.policy_version == policy['policy_version']
