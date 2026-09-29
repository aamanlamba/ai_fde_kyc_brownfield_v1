from src import rules


def test_bs01_policy_values_drive_rules():
    policy = {
        'policy_version': '1.0.0',
        'approved_by': 'Compliance KYC policy lead',
        'approved_on': '2026-09-28',
        'completeness_threshold': 1.0,
        'supported_types': ['passport', 'national_id', 'driving_licence'],
        'number_patterns': {
            'passport': '^PXT\\d{6}$',
            'national_id': '^MID-\\d{4}-\\d{4}$',
            'driving_licence': '^MDL-\\d{6}$',
        },
        'mandatory_fields': ['full_name', 'date_of_birth', 'document_number', 'expiry_date'],
    }
    original = rules.get_policy_source()
    rules.set_policy_source(lambda: policy)
    try:
        data = {'document_type': 'passport', 'full_name': 'A', 'date_of_birth': '1990-01-01', 'document_number': 'PXT123456'}
        decision, reasons, warnings = rules.evaluate(data, '')
        assert decision == 'REVIEW'
        assert 'INSUFFICIENT_MANDATORY_FIELDS' in reasons
    finally:
        rules.set_policy_source(original)
