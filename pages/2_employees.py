import pandas as pd
import streamlit as st
from sqlalchemy import select

from database import session_scope
from models import Employee
from services.hr_analyzer import department_headcount
from utils.layout import setup_page, toolbar, toolbar_label
from utils.session import company_selector, require_login
from utils.theme import PRIMARY_LIGHT, bar_chart, panel_end, panel_start

require_login()
setup_page("Сотрудники", "Справочник и структура по подразделениям")

with toolbar():
    toolbar_label("Организация")
    company_id = company_selector("emp_company")

with session_scope() as session:
    employees = session.scalars(
        select(Employee).where(Employee.company_id == company_id).order_by(Employee.name)
    ).all()
    dept_df = department_headcount(session, company_id)
    emp_df = pd.DataFrame(
        [
            {
                "ФИО": e.name,
                "Подразделение": e.department,
                "Должность": e.position,
                "Принят": e.hire_date.strftime("%d.%m.%Y"),
                "Уволен": e.termination_date.strftime("%d.%m.%Y") if e.termination_date else "—",
            }
            for e in employees
        ]
    )

table_col, chart_col = st.columns([3, 2])

with table_col:
    panel_start("Список сотрудников", f"всего: {len(emp_df)}")
    if not emp_df.empty:
        st.dataframe(emp_df, use_container_width=True, hide_index=True, height=480)
    else:
        st.info("Нет сотрудников. Импортируйте данные из 1С.")
    panel_end()

with chart_col:
    panel_start("Численность по отделам")
    if not dept_df.empty:
        fig = bar_chart(
            dept_df["department"].tolist(),
            dept_df["headcount"].tolist(),
            color=PRIMARY_LIGHT,
            height=420,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных")
    panel_end()
