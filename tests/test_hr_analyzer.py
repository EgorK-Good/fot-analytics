"""Тесты кадровой аналитики."""

from datetime import date

from services.hr_analyzer import department_headcount, headcount_by_month, hires_by_month


def test_department_headcount(session, company, employee, terminated_employee):
    df = department_headcount(session, company.id, on_date=date(2026, 1, 1))
    assert "department" in df.columns
    assert "headcount" in df.columns
    assert df["headcount"].sum() == 1
    it_row = df[df["department"] == "Отдел IT"]
    assert int(it_row["headcount"].iloc[0]) == 1


def test_department_headcount_empty(session, company):
    df = department_headcount(session, company.id, on_date=date(2020, 1, 1))
    assert df.empty
    assert list(df.columns) == ["department", "headcount"]


def test_headcount_by_month(session, company, employee):
    df = headcount_by_month(session, company.id, months=3)
    assert len(df) == 3
    assert "headcount" in df.columns
    assert df["headcount"].iloc[-1] >= 1


def test_hires_by_month(session, company, employee):
    df = hires_by_month(session, company.id, months=24)
    assert len(df) == 24
    assert "hires" in df.columns
    hire_month = employee.hire_date.replace(day=1)
    month_rows = df[df["ds"].dt.date == hire_month]
    if not month_rows.empty:
        assert int(month_rows["hires"].iloc[0]) >= 1
