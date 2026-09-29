from __future__ import annotations

from datetime import date

from src.ports import Clock


class SystemClock(Clock):
    def today(self) -> date:
        return date.today()


class FixedClock(Clock):
    def __init__(self, fixed_date: date):
        self._fixed_date = fixed_date

    def today(self) -> date:
        return self._fixed_date
