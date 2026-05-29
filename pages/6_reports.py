import streamlit as st

from database import session_scope
from services.fot_analyzer import month_bounds
from services.report_service import generate_fot_report
from utils.layout import period_selector, setup_page, toolbar, toolbar_label
from utils.session import company_selector, require_login
from utils.theme import panel_end, panel_start

require_login()
setup_page("Отчёты", "Выгрузка в Excel")

with toolbar():
    c1, c2 = st.columns(2)
    with c1:
        toolbar_label("Организация")
        company_id = company_selector("report_company")
    with c2:
        toolbar_label("Период")
        year, month = period_selector("report_period")

start, end = month_bounds(year, month)

panel_start("ФОТ-отчёт", "подразделения, динамика, текучесть")
st.markdown(
    "Содержит: ФОТ по отделам, динамику, текучесть, структуру выплат."
)

if st.button("Сформировать", type="primary"):
    with session_scope() as session:
        data = generate_fot_report(session, company_id, start, end)
    st.download_button(
        "Скачать Excel",
        data=data,
        file_name=f"fot_report_{year}_{month:02d}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
panel_end()
