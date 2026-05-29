import plotly.graph_objects as go
import streamlit as st

from database import session_scope
from services.advanced_analytics import AdvancedAnalyticsService
from services.kpi_service import (
    get_dashboard_kpi,
    get_department_structure,
    get_fot_dynamics_chart_data,
    get_salary_bins,
)
from utils.layout import (
    delta_type_from_pct,
    format_money,
    format_pct,
    period_selector,
    render_kpi_row,
    setup_page,
    toolbar,
    toolbar_label,
)
from utils.session import company_selector, require_login
from utils.theme import CHART_COLORS, PRIMARY_LIGHT, ROSE, apply_chart_style, chip_row, panel_end, panel_start

require_login()
setup_page("Главная", "Сводка по фонду оплаты труда")

with toolbar():
    t1, t2 = st.columns([2, 1])
    with t1:
        toolbar_label("Организация")
        company_id = company_selector("home_company")
    with t2:
        toolbar_label("Отчётный период")
        year, month = period_selector("home_period")

with session_scope() as session:
    kpi = get_dashboard_kpi(session, company_id, year, month)
    dynamics = get_fot_dynamics_chart_data(session, company_id, 12)
    dept_df = get_department_structure(session, company_id, year, month)
    salary_bins = get_salary_bins(session, company_id, year, month)
    productivity = AdvancedAnalyticsService.get_productivity_metrics(session, company_id, year, month)

fot_delta_type = "negative" if kpi.fot_change_pct and kpi.fot_change_pct < 0 else "positive"
avg_delta_type = delta_type_from_pct(kpi.avg_change_pct)
hc_delta = (
    "без изменений"
    if kpi.headcount_change == 0
    else f"{'+' if kpi.headcount_change > 0 else ''}{kpi.headcount_change} чел."
)
hc_type = "neutral" if kpi.headcount_change == 0 else ("positive" if kpi.headcount_change > 0 else "negative")

render_kpi_row(
    [
        ("ФОТ за месяц", format_money(kpi.total_fot), format_pct(kpi.fot_change_pct), fot_delta_type),
        ("Средняя зарплата", format_money(kpi.avg_salary), format_pct(kpi.avg_change_pct), avg_delta_type),
        ("Численность", f"{kpi.headcount}", hc_delta, hc_type),
        ("ФОТ / сотрудник", format_money(productivity["fot_per_employee"]), f"присутствие {productivity['attendance_rate']:.0f}%", "neutral"),
    ]
)

chip_row(
    [
        ("Премии", format_money(kpi.total_bonus)),
        ("Отпускные", format_money(kpi.total_vacation)),
        ("НДФЛ", format_money(kpi.total_ndfl)),
        ("Период", f"{year}-{month:02d}"),
    ]
)

chart_main, chart_side = st.columns([7, 5])

with chart_main:
    panel_start("Динамика ФОТ", "последние 12 месяцев")
    if not dynamics.empty:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dynamics["ds"],
                y=dynamics["total_fot"],
                name="ФОТ",
                fill="tozeroy",
                fillcolor="rgba(184, 169, 201, 0.15)",
                line=dict(color=PRIMARY_LIGHT, width=2.5, shape="spline"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dynamics["ds"],
                y=dynamics["bonus"],
                name="Премии",
                line=dict(color=ROSE, width=2, shape="spline"),
            )
        )
        apply_chart_style(fig, height=360)
        fig.update_layout(yaxis_title="₽")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Загрузите данные из 1С или добавьте демо-набор")
    panel_end()

with chart_side:
    panel_start("По подразделениям", "доля ФОТ")
    if not dept_df.empty:
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=dept_df["department"],
                    values=dept_df["fot"],
                    hole=0.55,
                    marker=dict(colors=CHART_COLORS, line=dict(color="#fff", width=1)),
                    textinfo="percent",
                )
            ]
        )
        apply_chart_style(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нет данных за период")
    panel_end()

panel_start("Распределение окладов", f"{year}-{month:02d}")
if not salary_bins.empty:
    fig = go.Figure(data=[go.Bar(x=salary_bins["range"], y=salary_bins["count"], marker_color=PRIMARY_LIGHT)])
    apply_chart_style(fig, height=280)
    fig.update_layout(xaxis_title="Диапазон", yaxis_title="Сотрудников")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Нет данных за период")
panel_end()
