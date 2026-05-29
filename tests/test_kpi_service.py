"""Тесты KPI главной панели."""

from services.kpi_service import get_dashboard_kpi, get_department_structure


def test_get_dashboard_kpi(session, company, employee, salary_records):
    kpi = get_dashboard_kpi(session, company.id, year=2026, month=2)
    assert kpi.total_fot == 130_000.0
    assert kpi.headcount == 1
    assert kpi.total_bonus == 20_000.0
    assert kpi.total_vacation == 0.0
    assert kpi.fot_change_pct is not None


def test_get_dashboard_kpi_no_data(session, company):
    kpi = get_dashboard_kpi(session, company.id, year=2020, month=1)
    assert kpi.total_fot == 0.0
    assert kpi.headcount == 0
    assert kpi.fot_change_pct is None


def test_get_department_structure(session, company, salary_records):
    df = get_department_structure(session, company.id, year=2026, month=2)
    assert not df.empty
    assert df.loc[df["department"] == "Отдел IT", "fot"].iloc[0] == 130_000.0
