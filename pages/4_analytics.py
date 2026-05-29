import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import date, timedelta

from database import session_scope
from services.advanced_analytics import AdvancedAnalyticsService
from services.forecast_service import forecast_summary_table, predict_fot_horizon
from services.hr_forecast_service import forecast_headcount, forecast_turnover
from utils.charts import (
    fot_forecast_chart,
    headcount_forecast_chart,
    horizontal_bar,
    turnover_forecast_chart,
)
from utils.layout import (
    format_money,
    period_selector,
    render_stat_row,
    setup_page,
    toolbar,
    toolbar_label,
)
from utils.session import company_selector, require_login
from utils.theme import (
    CHART_COLORS,
    PRIMARY_LIGHT,
    ROSE,
    apply_chart_style,
    chip_row,
    donut_chart,
    panel_end,
    panel_start,
)

require_login()
setup_page("Аналитика", "Прогнозы, структура ФОТ и кадровые показатели")

with toolbar():
    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
    with c1:
        toolbar_label("Организация")
        company_id = company_selector("analytics_company")
    with c2:
        toolbar_label("Период с")
        start_date = st.date_input(
            "С",
            value=date.today() - timedelta(days=365),
            max_value=date.today(),
            label_visibility="collapsed",
            key="an_start",
        )
    with c3:
        toolbar_label("по")
        end_date = st.date_input(
            "По",
            value=date.today(),
            max_value=date.today(),
            label_visibility="collapsed",
            key="an_end",
        )
    with c4:
        toolbar_label("Месяц ФОТ")
        year, month = period_selector("analytics_fot_period")
    with c5:
        toolbar_label("Прогноз, мес.")
        forecast_months = st.slider("М", 1, 12, 6, label_visibility="collapsed", key="an_horizon")

with session_scope() as session:
    fot_df = predict_fot_horizon(session, company_id, forecast_months)
    hc_fc = forecast_headcount(session, company_id, forecast_months)
    to_fc = forecast_turnover(session, company_id, forecast_months)
    absence_data = AdvancedAnalyticsService.get_absence_analytics(session, company_id, start_date, end_date)
    overtime_data = AdvancedAnalyticsService.get_overtime_analytics(session, company_id, start_date, end_date)
    schedule_data = AdvancedAnalyticsService.get_work_schedule_analytics(session, company_id)
    salary_data = AdvancedAnalyticsService.get_salary_composition_analytics(session, company_id, year, month)
    turnover_data = AdvancedAnalyticsService.get_employee_turnover_analytics(session, company_id, start_date, end_date)
    productivity_data = AdvancedAnalyticsService.get_productivity_metrics(session, company_id, year, month)

total_absence = sum(x["total_days"] for x in absence_data.get("by_type", []))
hist_months = len(fot_df[fot_df["type"] == "История"]) if not fot_df.empty else 0

render_stat_row(
    [
        ("ФОТ (месяц)", format_money(salary_data["total_fot"]), f"{year}-{month:02d}", "mauve"),
        ("Прогноз ФОТ", format_money(fot_df[fot_df["type"] == "Прогноз"]["yhat"].iloc[0]) if not fot_df[fot_df["type"] == "Прогноз"].empty else "—", f"+{forecast_months} мес.", "rose"),
        ("Отсутствия", f"{total_absence:.0f} дн.", "за период", "sky"),
        ("Текучесть", f"{turnover_data['turnover_rate']:.1f}%", "за период", "sage"),
    ]
)

tab_fc, tab_fot, tab_abs, tab_ot, tab_sched, tab_hr = st.tabs(
    ["Прогноз", "Состав ФОТ", "Отсутствия", "Переработки", "Графики работы", "Кадры"]
)

# ——— Прогноз ———
with tab_fc:
    st.caption(
        "Прогноз строится по помесячному ФОТ (оклад + премии + отпускные + больничные + переработки). "
        f"История: **{hist_months}** мес. "
        + ("Модель Prophet с сезонностью." if hist_months >= 24 else "Упрощённый тренд (мало истории).")
    )

    if fot_df.empty or hist_months < 2:
        st.warning("Для прогноза нужно минимум 2 месяца с начислениями.")
    else:
        panel_start("Прогноз фонда оплаты труда", "факт · пунктир — прогноз · зона — 85% интервал")
        st.plotly_chart(fot_forecast_chart(fot_df), use_container_width=True)
        panel_end()

        summary = forecast_summary_table(fot_df)
        if not summary.empty:
            panel_start("Помесячный прогноз")
            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Прогноз": st.column_config.NumberColumn(format="%d ₽"),
                    "Нижняя_граница": st.column_config.NumberColumn("Мин.", format="%d ₽"),
                    "Верхняя_граница": st.column_config.NumberColumn("Макс.", format="%d ₽"),
                },
            )
            panel_end()

    c1, c2 = st.columns(2)
    with c1:
        panel_start("Численность", "чел. на конец месяца")
        if hc_fc.empty:
            st.info("Недостаточно данных")
        else:
            st.plotly_chart(headcount_forecast_chart(hc_fc), use_container_width=True)
        panel_end()
    with c2:
        panel_start("Текучесть", "% увольнений от численности")
        if to_fc.empty:
            st.info("Недостаточно данных")
        else:
            st.plotly_chart(turnover_forecast_chart(to_fc), use_container_width=True)
        panel_end()

# ——— Состав ФОТ ———
with tab_fot:
    if not salary_data["components"]:
        st.info("Нет начислений за выбранный месяц")
    else:
        left, right = st.columns([3, 2])
        with left:
            panel_start(f"Структура выплат · {year}-{month:02d}")
            fig = donut_chart(
                [x["name"] for x in salary_data["components"]],
                [x["value"] for x in salary_data["components"]],
                height=360,
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
            panel_end()
        with right:
            panel_start("Доли компонентов")
            st.metric("Итого ФОТ", format_money(salary_data["total_fot"]))
            st.metric("НДФЛ удержано", format_money(salary_data["total_ndfl"]))
            for c in sorted(salary_data["components"], key=lambda x: -x["value"]):
                st.progress(
                    float(c["percentage"]) / 100,
                    text=f"{c['name']}: {format_money(c['value'])} ({float(c['percentage']):.1f}%)",
                )
            panel_end()

# ——— Отсутствия ———
with tab_abs:
    if not absence_data["by_type"]:
        st.info("Нет данных об отсутствиях за период")
    else:
        types = absence_data["by_type"]
        c1, c2 = st.columns(2)
        with c1:
            panel_start("Дни по типам отсутствия")
            fig = horizontal_bar(
                [x["type"] for x in types],
                [x["total_days"] for x in types],
                "",
                color=PRIMARY_LIGHT,
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)
            panel_end()
        with c2:
            panel_start("Случаи по месяцам")
            if absence_data["monthly_trend"]:
                df = pd.DataFrame(absence_data["monthly_trend"])
                pivot = df.pivot(index="month", columns="type", values="count").fillna(0)
                fig = go.Figure()
                for i, col in enumerate(pivot.columns):
                    fig.add_trace(
                        go.Bar(
                            name=col,
                            x=pivot.index.astype(str),
                            y=pivot[col],
                            marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                        )
                    )
                apply_chart_style(fig, height=280)
                fig.update_layout(barmode="stack", xaxis_title="Месяц", yaxis_title="Случаев")
                st.plotly_chart(fig, use_container_width=True)
            panel_end()
        panel_start("Сводная таблица")
        st.dataframe(
            pd.DataFrame(types),
            use_container_width=True,
            hide_index=True,
            column_config={
                "type": "Тип",
                "count": "Случаев",
                "total_days": "Дней",
                "avg_days": st.column_config.NumberColumn("Ср. дней", format="%.1f"),
            },
        )
        panel_end()

# ——— Переработки ———
with tab_ot:
    if not overtime_data["by_department"]:
        st.info("Нет переработок за период")
    else:
        depts = overtime_data["by_department"]
        c1, c2 = st.columns(2)
        with c1:
            panel_start("Часы по подразделениям")
            fig = horizontal_bar(
                [x["department"] for x in depts],
                [x["total_hours"] for x in depts],
                "",
                color=PRIMARY_LIGHT,
                height=max(280, len(depts) * 36),
            )
            st.plotly_chart(fig, use_container_width=True)
            panel_end()
        with c2:
            panel_start("Топ-10 сотрудников")
            tops = overtime_data.get("top_employees") or []
            if tops:
                fig = horizontal_bar(
                    [x["name"] for x in tops],
                    [x["total_hours"] for x in tops],
                    "",
                    color=ROSE,
                    height=320,
                )
                st.plotly_chart(fig, use_container_width=True)
            panel_end()

# ——— Графики работы ———
with tab_sched:
    if not schedule_data["by_schedule"]:
        st.info("Нет данных о графиках")
    else:
        c1, c2 = st.columns(2)
        with c1:
            panel_start("Распределение по графикам")
            fig = donut_chart(
                [x["schedule"] for x in schedule_data["by_schedule"]],
                [x["count"] for x in schedule_data["by_schedule"]],
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)
            panel_end()
        with c2:
            panel_start("График × подразделение")
            if schedule_data["by_department"]:
                df = pd.DataFrame(schedule_data["by_department"])
                pivot = df.pivot(index="department", columns="schedule", values="count").fillna(0)
                fig = go.Figure(
                    data=go.Heatmap(
                        z=pivot.values,
                        x=[str(c) for c in pivot.columns],
                        y=[str(i) for i in pivot.index],
                        colorscale=[[0, "#F8F6FA"], [0.5, "#DDD2E6"], [1, "#B8A9C9"]],
                        text=pivot.values,
                        texttemplate="%{text}",
                        colorbar=dict(title="чел."),
                    )
                )
                apply_chart_style(fig, height=300)
                fig.update_layout(xaxis_title="График", yaxis_title="Подразделение")
                st.plotly_chart(fig, use_container_width=True)
            panel_end()

# ——— Кадры ———
with tab_hr:
    chip_row(
        [
            ("Уволено", str(turnover_data["terminated_count"])),
            ("Принято", str(turnover_data["hired_count"])),
            ("Чистое Δ", str(turnover_data["net_change"])),
            ("Ср. стаж увол.", f"{turnover_data['avg_tenure_days']:.0f} дн." if turnover_data["avg_tenure_days"] else "—"),
        ]
    )
    render_stat_row(
        [
            ("Текучесть", f"{turnover_data['turnover_rate']:.1f}%", "за период", "sand"),
            ("Присутствие", f"{productivity_data['attendance_rate']:.1f}%", f"{year}-{month:02d}", "sky"),
            ("ФОТ / чел.", format_money(productivity_data["fot_per_employee"]), "месяц", "mauve"),
            ("В расчёте", str(productivity_data["employee_count"]), "сотрудников", "rose"),
        ]
    )
