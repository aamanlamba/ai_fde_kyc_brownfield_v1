from src.service import verify_document


def test_TST_13_012_unsupported_type_reviews():
    result = verify_document('CASE-001-PASSPORT')
    assert result.decision == 'APPROVE'
    raw = {'document_type': 'RESIDENCE_PERMIT', 'full_name': 'A', 'date_of_birth': '1990-01-01', 'document_number': 'PXT123456', 'expiry_date': '2035-01-01'}
    from src import rules
    original = rules.get_policy_source()
    rules.set_policy_source(lambda: {'policy_version': '1.1.0', 'approved_by': 'Compliance KYC policy lead', 'approved_on': '2026-09-29', 'completeness_threshold': 0.75, 'supported_types': ['passport', 'national_id', 'driving_licence'], 'number_patterns': {'passport': '^PXT\\d{6}$', 'national_id': '^MID-\\d{4}-\\d{4}$', 'driving_licence': '^MDL-\\d{6}$'}, 'mandatory_fields': ['full_name', 'date_of_birth', 'document_number', 'expiry_date'], 'label_aliases': {'NAME': ['FULL NAME']}})
    try:
        decision, reasons, _ = rules.evaluate(raw, '')
        assert decision == 'REVIEW'
        assert 'UNSUPPORTED_DOCUMENT_TYPE' in reasons
    finally:
        rules.set_policy_source(original)
