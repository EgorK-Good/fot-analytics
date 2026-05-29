from calendar import monthrange
from datetime import date

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import Employee, SalaryHistory


def _salary_df(session: Session, company_id: int, start: date, end: date) -> pd.DataFrame:
    rows = session.scalars(
        select(SalaryHistory)
        .join(Employee)
        .where(
            Employee.company_id == company_id,
            SalaryHistory.date >= start,
            SalaryHistory.date <= end,
        )
        .options(joinedload(SalaryHistory.employee))
    ).all()
    if not rows:
        return pd.DataFrame(
            columns=["employee_id", "department", "fot", "salary", "bonus", "vacation_pay", "ndfl", "date"]
        )
    return pd.DataFrame(
        [
            {
                "employee_id": r.employee_id,
                "department": r.employee.department,
                "fot": float(r.salary) + float(r.bonus) + float(r.vacation_pay) + float(r.sick_leave_pay) + float(r.overtime_pay),
                "salary": float(r.salary),
                "bonus": float(r.bonus),
                "vacation_pay": float(r.vacation_pay),
                "ndfl": float(r.ndfl),
                "date": r.date,
            }
            for r in rows
        ]
    )


def get_monthly_fot_df(session: Session, company_id: int, months: int = 12) -> pd.DataFrame:
    """Помесячный ФОТ, премии и отпускные для графика динамики."""
    rows = session.scalars(
        select(SalaryHistory)
        .join(Employee)
        .where(Employee.company_id == company_id)
        .order_by(SalaryHistory.date)
    ).all()
    if not rows:
        return pd.DataFrame(columns=["ds", "total_fot", "bonus", "vacation_pay"])

    df = pd.DataFrame(
        [
            {
                "ds": pd.Timestamp(r.date),
                "total_fot": float(r.salary) + float(r.bonus) + float(r.vacation_pay) + float(r.sick_leave_pay) + float(r.overtime_pay),
                "bonus": float(r.bonus),
                "vacation_pay": float(r.vacation_pay),
            }
            for r in rows
        ]
    )
    monthly = (
        df.groupby(pd.Grouper(key="ds", freq="MS"))
        .agg({"total_fot": "sum", "bonus": "sum", "vacation_pay": "sum"})
        .reset_index()
        .tail(months)
    )
    return monthly


def get_salary_distribution(session: Session, company_id: int, start: date, end: date) -> pd.DataFrame:
    df = _salary_df(session, company_id, start, end)
    if df.empty:
        return pd.DataFrame(columns=["range", "count"])

    latest = df.sort_values("date").groupby("employee_id").last().reset_index()
    bins = [0, 50000, 80000, 100000, 150000, 200000, float("inf")]
    labels = ["до 50 тыс.", "50–80 тыс.", "80–100 тыс.", "100–150 тыс.", "150–200 тыс.", "200+ тыс."]
    latest["range"] = pd.cut(latest["salary"], bins=bins, labels=labels, right=False)
    dist = latest.groupby("range", observed=False).size().reset_index(name="count")
    dist.columns = ["range", "count"]
    return dist


def calculate_fot_by_department(
    session: Session, company_id: int, start: date, end: date
) -> dict[str, float]:
    df = _salary_df(session, company_id, start, end)
    if df.empty:
        return {}
    grouped = df.groupby("department")["fot"].sum()
    return {k: float(v) for k, v in grouped.items()}


def calculate_salary_trend(session: Session, company_id: int, year: int) -> dict[str, float]:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    df = _salary_df(session, company_id, start, end)
    if df.empty:
        return {}
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
    grouped = df.groupby("month")["fot"].sum().sort_index()
    return {k: float(v) for k, v in grouped.items()}


def calculate_turnover(
    session: Session, company_id: int, start: date, end: date
) -> dict[str, int]:
    employees = session.scalars(
        select(Employee).where(
            Employee.company_id == company_id,
            Employee.termination_date.isnot(None),
            Employee.termination_date >= start,
            Employee.termination_date <= end,
        )
    ).all()
    if not employees:
        return {}
    result: dict[str, int] = {}
    for emp in employees:
        key = emp.termination_date.strftime("%Y-%m") if emp.termination_date else "Active"
        result[key] = result.get(key, 0) + 1
    return result


def calculate_salary_bonus_ratio(
    session: Session, company_id: int, start: date, end: date
) -> dict[str, float]:
    df = _salary_df(session, company_id, start, end)
    if df.empty:
        return {"Оклады": 0.0, "Премии": 0.0, "Отпускные": 0.0}
    return {
        "Оклады": float(df["salary"].sum()),
        "Премии": float(df["bonus"].sum()),
        "Отпускные": float(df["vacation_pay"].sum()),
    }


def month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end
