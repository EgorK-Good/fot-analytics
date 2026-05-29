"""Тесты расчёта ФОТ."""

from datetime import date

from services.fot_analyzer import (
    calculate_fot_by_department,
    calculate_salary_bonus_ratio,
    calculate_salary_trend,
    calculate_turnover,
    get_monthly_fot_df,
    get_salary_distribution,
    month_bounds,
)


def test_month_bounds():
    start, end = month_bounds(2026, 2)
    assert start == date(2026, 2, 1)
    assert end == date(2026, 2, 28)


def test_calculate_fot_by_department(session, company, salary_records):
    by_dept = calculate_fot_by_department(
        session, company.id, date(2025, 1, 1), date(2026, 12, 31)
    )
    assert "Отдел IT" in by_dept
    # 115000 + 128000 + 130000
    assert by_dept["Отдел IT"] == 373_000.0


def test_calculate_fot_by_department_empty(session, company):
    assert calculate_fot_by_department(
        session, company.id, date(2020, 1, 1), date(2020, 12, 31)
    ) == {}


def test_calculate_salary_bonus_ratio(session, company, salary_records):
    ratio = calculate_salary_bonus_ratio(
        session, company.id, date(2025, 1, 1), date(2026, 12, 31)
    )
    assert ratio["Оклады"] == 310_000.0
    assert ratio["Премии"] == 45_000.0
    assert ratio["Отпускные"] == 8_000.0


def test_calculate_salary_trend(session, company, salary_records):
    trend = calculate_salary_trend(session, company.id, 2026)
    assert "2026-01" in trend
    assert "2026-02" in trend
    assert trend["2026-02"] == 130_000.0


def test_calculate_turnover(session, company, terminated_employee):
    turnover = calculate_turnover(
        session, company.id, date(2025, 1, 1), date(2025, 12, 31)
    )
    assert turnover.get("2025-03", 0) == 1


def test_get_monthly_fot_df(session, company, salary_records):
    df = get_monthly_fot_df(session, company.id, months=12)
    assert not df.empty
    assert "total_fot" in df.columns
    assert df["total_fot"].sum() == 373_000.0


def test_get_salary_distribution(session, company, salary_records):
    dist = get_salary_distribution(
        session, company.id, date(2025, 1, 1), date(2026, 12, 31)
    )
    assert not dist.empty
    assert dist["count"].sum() == 1
