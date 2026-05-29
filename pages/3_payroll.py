import pandas as pd
import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database import session_scope
from models import Employee, SalaryHistory
from services.fot_analyzer import month_bounds
from utils.layout import format_money, period_selector, render_stat_row, setup_page, toolbar, toolbar_label
from utils.session import company_selector, require_login
from utils.theme import panel_end, panel_start

require_login()
setup_page("Начисления", "Выплаты за выбранный месяц")

with toolbar():
    c1, c2 = st.columns(2)
    with c1:
        toolbar_label("Организация")
        company_id = company_selector("acc_company")
    with c2:
        toolbar_label("Период")
        year, month = period_selector("acc_period")

start, end = month_bounds(year, month)

with session_scope() as session:
    rows = session.scalars(
        select(SalaryHistory)
        .join(Employee)
        .where(
            Employee.company_id == company_id,
            SalaryHistory.date >= start,
            SalaryHistory.date <= end,
        )
        .options(joinedload(SalaryHistory.employee))
        .order_by(SalaryHistory.date.desc())
    ).all()
    df = pd.DataFrame(
        [
            {
                "Сотрудник": r.employee.name,
                "Подразделение": r.employee.department,
                "Оклад": float(r.salary),
                "Премия": float(r.bonus),
                "Отпускные": float(r.vacation_pay),
                "НДФЛ": float(r.ndfl),
                "ФОТ": float(r.salary) + float(r.bonus) + float(r.vacation_pay)
                + float(r.sick_leave_pay or 0) + float(r.overtime_pay or 0),
            }
            for r in rows
        ]
    )

total_fot = df["ФОТ"].sum() if not df.empty else 0
render_stat_row(
    [
        ("Итого ФОТ", format_money(total_fot), f"{year}-{month:02d}", "mauve"),
        ("Записей", str(len(df)), "начислений", "sky"),
        ("Средний ФОТ", format_money(total_fot / len(df)) if len(df) else "0 ₽", "на запись", "rose"),
        ("НДФЛ", format_money(df["НДФЛ"].sum()) if not df.empty else 0, "удержано", "sand"),
    ]
)

panel_start(f"Реестр начислений · {year}-{month:02d}")
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Нет начислений за выбранный период")
panel_end()
