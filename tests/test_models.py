"""Тесты модели данных."""

from datetime import date

from models import SalaryHistory


def test_salary_history_fot_property():
    row = SalaryHistory(
        employee_id=1,
        salary=80_000,
        bonus=10_000,
        vacation_pay=5_000,
        sick_leave_pay=2_000,
        overtime_pay=3_000,
        ndfl=10_000,
        date=date(2026, 1, 1),
    )
    assert row.fot == 100_000.0
