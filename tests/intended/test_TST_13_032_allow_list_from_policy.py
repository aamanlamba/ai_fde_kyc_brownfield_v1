from src import service


def test_TST_13_032_allow_list_from_policy():
    original = service._POLICY

    class Policy:
        def get_policy(self):
            return {
                'policy_version': '1.1.0',
                'approved_by': 'Compliance KYC policy lead',
                'approved_on': '2026-09-29',
                'completeness_threshold': 0.75,
                'supported_types': ['passport', 'national_id'],
                'number_patterns': {'passport': '^PXT\\d{6}$', 'national_id': '^MID-\\d{4}-\\d{4}$'},
                'mandatory_fields': ['full_name', 'date_of_birth', 'document_number', 'expiry_date'],
                'label_aliases': {'NAME': ['FULL NAME'], 'DOCUMENT TYPE': ['DOC TYPE']},
            }

    service._POLICY = Policy()
    try:
        result = service.verify_document('CASE-001-DL')
        assert result.decision == 'REVIEW'
        assert 'UNSUPPORTED_DOCUMENT_TYPE' in result.reason_codes
    finally:
        service._POLICY = original
