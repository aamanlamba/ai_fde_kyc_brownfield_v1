from src.models import DocumentResult


def test_bs02_legacy_projection_unchanged():
    result = DocumentResult(
        document_id='CASE-001',
        document_type='passport',
        decision='APPROVE',
        reason_codes=['BASELINE_RULES_PASSED'],
        parsed_fields={'full_name': 'Aarav Mehta'},
        completeness=1.0,
        warnings=[],
        missing_fields=[],
        policy_version='1.1.0',
    )
    assert result.document_id == 'CASE-001'
    assert result.document_type == 'passport'
    assert result.decision == 'APPROVE'
    assert result.parsed_fields['full_name'] == 'Aarav Mehta'
