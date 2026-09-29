from src.rules import evaluate


def test_TST_13_009_unparsed_line_reaches_rules():
    decision, reasons, warnings = evaluate({'document_type': 'passport', 'full_name': 'A', 'date_of_birth': '1990-01-01', 'document_number': 'PXT123456', 'expiry_date': '2035-01-01'}, 'FOO BAR: x\nCUSTOM NOTE: value')
    assert decision == 'REVIEW'
    assert 'UNREAD_EVIDENCE' in reasons
