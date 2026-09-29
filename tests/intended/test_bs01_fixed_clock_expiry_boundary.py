from datetime import date

from src.adapters.clocks import FixedClock
from src.rules import evaluate


def test_TST_13_014_expiry_boundary():
    fields = {
        'document_type': 'passport',
        'full_name': 'A',
        'date_of_birth': '1990-01-01',
        'document_number': 'PXT123456',
        'expiry_date': '2026-09-09',
    }

    decision, reasons, _ = evaluate(fields, '', clock=FixedClock(date(2026, 9, 9)))
    assert decision == 'APPROVE'
    assert 'DOCUMENT_EXPIRED' not in reasons

    fields['expiry_date'] = '2026-09-08'
    decision, reasons, _ = evaluate(fields, '', clock=FixedClock(date(2026, 9, 9)))
    assert decision == 'REJECT'
    assert 'DOCUMENT_EXPIRED' in reasons
