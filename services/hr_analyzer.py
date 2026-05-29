"""Кадровая аналитика: численность, текучесть, приём/увольнение."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Employee


def headcount_by_month(session: Session, company_id: int, months: int = 24) -> pd.DataFrame:
    """Численность на конец каждого месяца."""
    today = date.today()
    periods = pd.date_range(end=today.replace(day=1), periods=months, freq="MS")
    rows = []
    for period in periods:
        month_end = (period + pd.offsets.MonthEnd(0)).date()
        count = session.scalar(
            select(func.count())
            .select_from(Employee)
            .where(
                Employee.company_id == company_id,
                Employee.hire_date <= month_end,
                (Employee.termination_date.is_(None)) | (Employee.termination_date > month_end),
            )
        )
        rows.append({"ds": period, "headcount": count or 0})
    return pd.DataFrame(rows)


def turnover_by_month(session: Session, company_id: int, months: int = 24) -> pd.DataFrame:
    """Увольнения и текучесть по месяцам."""
    today = date.today()
    periods = pd.date_range(end=today.replace(day=1), periods=months, freq="MS")
    rows = []
    for period in periods:
        month_start = period.date()
        month_end = (period + pd.offsets.MonthEnd(0)).date()
        terminations = session.scalar(
            select(func.count())
            .select_from(Employee)
            .where(
                Employee.company_id == company_id,
                Employee.termination_date.isnot(None),
                Employee.termination_date >= month_start,
                Employee.termination_date <= month_end,
            )
        ) or 0
        headcount = session.scalar(
            select(func.count())
            .select_from(Employee)
            .where(
                Employee.company_id == company_id,
                Employee.hire_date <= month_end,
                (Employee.termination_date.is_(None)) | (Employee.termination_date > month_end),
            )
        ) or 0
        rate = (terminations / headcount * 100) if headcount else 0.0
        rows.append({"ds": period, "terminations": terminations, "turnover_pct": rate})
    return pd.DataFrame(rows)


def hires_by_month(session: Session, company_id: int, months: int = 24) -> pd.DataFrame:
    today = date.today()
    periods = pd.date_range(end=today.replace(day=1), periods=months, freq="MS")
    rows = []
    for period in periods:
        month_start = period.date()
        month_end = (period + pd.offsets.MonthEnd(0)).date()
        hires = session.scalar(
            select(func.count())
            .select_from(Employee)
            .where(
                Employee.company_id == company_id,
                Employee.hire_date >= month_start,
                Employee.hire_date <= month_end,
            )
        ) or 0
        rows.append({"ds": period, "hires": hires})
    return pd.DataFrame(rows)


def department_headcount(session: Session, company_id: int, on_date: date | None = None) -> pd.DataFrame:
    on_date = on_date or date.today()
    employees = session.scalars(
        select(Employee).where(
            Employee.company_id == company_id,
            Employee.hire_date <= on_date,
            (Employee.termination_date.is_(None)) | (Employee.termination_date > on_date),
        )
    ).all()
    if not employees:
        return pd.DataFrame(columns=["department", "headcount"])
    df = pd.DataFrame([{"department": e.department, "headcount": 1} for e in employees])
    return df.groupby("department", as_index=False)["headcount"].sum()
