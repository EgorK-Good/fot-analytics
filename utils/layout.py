from contextlib import contextmanager
from datetime import datetime

import streamlit as st

from utils.pages_routing import NAV_ITEMS
from utils.session import init_session_state, logout
from utils.theme import apply_theme, kpi_card, soft_stat_card


def format_money(value: float) -> str:
    return f"{value:,.0f} ₽".replace(",", " ")


def format_pct(value: float | None) -> str:
    if value is None:
        return "нет данных"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}% к прошл. месяцу"


def delta_type_from_pct(value: float | None) -> str:
    if value is None:
        return "neutral"
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def render_sidebar_brand() -> None:
    st.markdown(
        """
        <div class="brand-title">Клиент+</div>
        <div class="brand-subtitle">Аналитика ФОТ и кадров</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_nav() -> None:
    for path, label in NAV_ITEMS:
        st.page_link(path, label=label)


def render_page_hero(title: str, subtitle: str = "") -> None:
    today = datetime.now().strftime("%d.%m.%Y")
    sub_html = f'<p class="page-hero-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-hero">
            <div>
                <h1 class="page-hero-title">{title}</h1>
                {sub_html}
            </div>
            <div class="page-hero-date">{today}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def toolbar():
    st.markdown('<div class="toolbar-card">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


def toolbar_label(text: str) -> None:
    st.markdown(f'<div class="toolbar-label">{text}</div>', unsafe_allow_html=True)


def period_selector(key: str = "period") -> tuple[int, int]:
    period = st.selectbox(
        "Период",
        options=[
            "2026-04", "2026-03", "2026-02", "2026-01",
            "2025-12", "2025-11", "2025-10", "2025-09",
            "2025-08", "2025-07", "2025-06", "2025-05",
        ],
        index=0,
        key=key,
        label_visibility="collapsed",
    )
    year, month = map(int, period.split("-"))
    return year, month


def setup_page(title: str, subtitle: str = "") -> None:
    init_session_state()
    apply_theme()
    with st.sidebar:
        render_sidebar_brand()
        if st.session_state.get("logged_in"):
            render_sidebar_nav()
            st.markdown("---")
            st.markdown(
                f"""
                <div class="sidebar-user">
                    <strong>{st.session_state.username}</strong>
                    Роль: {st.session_state.role}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.session_state.get("last_auto_import"):
                st.caption(st.session_state.last_auto_import)
            if st.button("Выйти", use_container_width=True, key="global_logout"):
                logout()
                st.switch_page("app.py")
    render_page_hero(title, subtitle)


def render_kpi_row(kpis: list[tuple[str, str, str, str]]) -> None:
    cols = st.columns(len(kpis))
    for col, (label, value, delta, dtype) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(label, value, delta, dtype), unsafe_allow_html=True)


def render_stat_row(stats: list[tuple[str, str, str, str]]) -> None:
    cols = st.columns(len(stats))
    for col, (label, value, hint, variant) in zip(cols, stats):
        with col:
            st.markdown(soft_stat_card(label, value, hint, variant), unsafe_allow_html=True)


def render_gradient_kpi_row(kpis: list[tuple[str, str, str, str]]) -> None:
    render_stat_row(kpis)


def render_page_header(breadcrumb: str) -> None:
    render_page_hero(breadcrumb)
