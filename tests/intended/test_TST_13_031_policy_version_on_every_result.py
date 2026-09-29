from src.adapters.file_policy_source import FilePolicySource
from src.service import verify_case


def test_TST_13_031_policy_version_on_every_result():
    policy = FilePolicySource().get_policy()
    for case_id in ('CASE-001', 'CASE-002', 'CASE-003', 'CASE-004', 'CASE-005', 'CASE-006'):
        case = verify_case(case_id)
        assert case.policy_version == policy['policy_version']
        for document in case.documents:
            assert document.policy_version == policy['policy_version']
