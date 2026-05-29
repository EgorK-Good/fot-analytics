"""KPI для главной панели (как в 1С:Аналитика ФОТ)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Employee, SalaryHistory
from services.fot_analyzer import get_monthly_fot_df, get_salary_distribution


@dataclass
class DashboardKPI:
    total_fot: float
    fot_change_pct: float | None
    avg_salary: float
    avg_change_pct: float | None
    headcount: int
    headcount_change: int
    turnover_pct: float
    total_ndfl: float
    total_bonus: float
    total_vacation: float


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    from services.fot_analyzer import month_bounds

    return month_bounds(year, month)


def get_dashboard_kpi(session: Session, company_id: int, year: int, month: int) -> DashboardKPI:
    start, end = _month_bounds(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_start, prev_end = _month_bounds(prev_year, prev_month)

    current = session.scalars(
        select(SalaryHistory)
        .join(Employee)
        .where(Employee.company_id == company_id, SalaryHistory.date >= start, SalaryHistory.date <= end)
    ).all()
    previous = session.scalars(
        select(SalaryHistory)
        .join(Employee)
        .where(
            Employee.company_id == company_id,
            SalaryHistory.date >= prev_start,
            SalaryHistory.date <= prev_end,
        )
    ).all()

    total_fot = sum(float(r.salary) + float(r.bonus) + float(r.vacation_pay) + float(r.sick_leave_pay) + float(r.overtime_pay) for r in current)
    prev_fot = sum(float(r.salary) + float(r.bonus) + float(r.vacation_pay) + float(r.sick_leave_pay) + float(r.overtime_pay) for r in previous)
    fot_change = ((total_fot - prev_fot) / prev_fot * 100) if prev_fot else None

    active_on = end
    headcount = session.scalar(
        select(func.count())
        .select_from(Employee)
        .where(
            Employee.company_id == company_id,
            Employee.hire_date <= active_on,
            (Employee.termination_date.is_(None)) | (Employee.termination_date > active_on),
        )
    ) or 0

    prev_active = prev_end
    prev_headcount = session.scalar(
        select(func.count())
        .select_from(Employee)
        .where(
            Employee.company_id == company_id,
            Employee.hire_date <= prev_active,
            (Employee.termination_date.is_(None)) | (Employee.termination_date > prev_active),
        )
    ) or 0

    avg_salary = (total_fot / headcount) if headcount else 0.0
    prev_avg = (prev_fot / prev_headcount) if prev_headcount else 0.0
    avg_change = ((avg_salary - prev_avg) / prev_avg * 100) if prev_avg else None

    terminations = session.scalar(
        select(func.count())
        .select_from(Employee)
        .where(
            Employee.company_id == company_id,
            Employee.termination_date.isnot(None),
            Employee.termination_date >= start,
            Employee.termination_date <= end,
        )
    ) or 0
    turnover_pct = (terminations / headcount * 100) if headcount else 0.0

    return DashboardKPI(
        total_fot=total_fot,
        fot_change_pct=fot_change,
        avg_salary=avg_salary,
        avg_change_pct=avg_change,
        headcount=headcount,
        headcount_change=headcount - prev_headcount,
        turnover_pct=turnover_pct,
        total_ndfl=sum(float(r.ndfl) for r in current),
        total_bonus=sum(float(r.bonus) for r in current),
        total_vacation=sum(float(r.vacation_pay) for r in current),
    )


def get_fot_dynamics_chart_data(session: Session, company_id: int, months: int = 12) -> pd.DataFrame:
    return get_monthly_fot_df(session, company_id, months)


def get_department_structure(session: Session, company_id: int, year: int, month: int) -> pd.DataFrame:
    start, end = _month_bounds(year, month)
    from services.fot_analyzer import calculate_fot_by_department

    data = calculate_fot_by_department(session, company_id, start, end)
    if not data:
        return pd.DataFrame(columns=["department", "fot"])
    return pd.DataFrame([{"department": k, "fot": v} for k, v in data.items()])


def get_salary_bins(session: Session, company_id: int, year: int, month: int) -> pd.DataFrame:
    start, end = _month_bounds(year, month)
    return get_salary_distribution(session, company_id, start, end)
