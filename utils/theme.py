"""Дизайн-система: мягкие пастельные акценты, карточная сетка."""

import streamlit as st

# Приглушённая палитра
PRIMARY = "#8E7C9E"
PRIMARY_LIGHT = "#B8A9C9"
ROSE = "#C9A0A8"
SAGE = "#8FAF9B"
SKY = "#7A9EB5"
SAND = "#B5A68A"
SLATE = "#64748B"
CHART_COLORS = ["#B8A9C9", "#C9A0A8", "#8FAF9B", "#7A9EB5", "#B5A68A", "#94A3B8"]

THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-app: #EEF1F5;
        --bg-card: #FFFFFF;
        --border: #E2E8F0;
        --text: #1E293B;
        --text-muted: #64748B;
        --accent: #9B8AA5;
        --accent-soft: #EDE8F2;
        --shadow: 0 1px 3px rgba(15, 23, 42, 0.05), 0 4px 16px rgba(15, 23, 42, 0.04);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background-color: var(--bg-app) !important;
    }

    /* Скрыть только меню «⋯» и Deploy; шапку оставляем — там кнопка разворота сайдбара */
    #MainMenu,
    [data-testid="stMainMenu"],
    .stDeployButton,
    footer {
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
    }

    header[data-testid="stHeader"] {
        visibility: visible !important;
        height: auto !important;
        min-height: 3.5rem !important;
        background: transparent !important;
    }

    /* Ссылки навигации в сайдбаре (st.page_link) */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        display: block;
        padding: 0.45rem 0.65rem;
        margin: 0.1rem 0;
        border-radius: 8px;
        color: var(--text) !important;
        text-decoration: none !important;
        font-size: 0.9rem;
        font-weight: 500;
    }

    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
        background: var(--accent-soft);
    }

    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
        background: var(--accent-soft);
        color: #5B4F66 !important;
        font-weight: 600;
    }

    .main .block-container {
        padding: 1rem 1.5rem 2rem;
        max-width: 1320px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(160deg, #F3EDF5 0%, #E8EEF4 55%, #EDE8F2 100%);
        padding: 1.35rem 1rem 1.25rem;
        margin: -0.5rem -0.5rem 0.5rem -0.5rem;
        border-bottom: 1px solid var(--border);
    }

    [data-testid="stSidebar"] .brand-title {
        color: #7A6B8A !important;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] .brand-subtitle {
        color: #334155 !important;
        font-size: 1.1rem;
        font-weight: 700;
    }

    [data-testid="stSidebar"] .sidebar-user {
        background: #F8FAFC;
        border-radius: 10px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border: 1px solid var(--border);
        font-size: 0.82rem;
        color: var(--text-muted);
    }

    [data-testid="stSidebar"] .sidebar-user strong {
        color: var(--text);
        display: block;
        margin-bottom: 0.15rem;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 0.25rem;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        border-radius: 8px;
        padding: 0.4rem 0.7rem;
        font-weight: 500;
        font-size: 0.88rem;
        color: var(--text-muted) !important;
        margin-bottom: 2px;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: var(--accent-soft) !important;
        color: #6B5B7A !important;
        font-weight: 600;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: #F8FAFC !important;
        border: 1px solid var(--border) !important;
        color: var(--text-muted) !important;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    /* Hero header */
    .page-hero {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 1rem;
        gap: 1rem;
    }

    .page-hero-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text);
        margin: 0;
        line-height: 1.25;
    }

    .page-hero-sub {
        font-size: 0.88rem;
        color: var(--text-muted);
        margin: 0.25rem 0 0;
    }

    .page-hero-date {
        font-size: 0.8rem;
        color: var(--text-muted);
        background: var(--bg-card);
        border: 1px solid var(--border);
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        white-space: nowrap;
        box-shadow: var(--shadow);
    }

    /* Toolbar */
    .toolbar-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.85rem 1rem 0.65rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }

    .toolbar-label {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #94A3B8;
        margin-bottom: 0.2rem;
    }

    /* Soft stat cards */
    .soft-stat {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: var(--shadow);
        height: 100%;
        min-height: 96px;
        position: relative;
        overflow: hidden;
    }

    .soft-stat::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        opacity: 0.85;
    }

    .soft-stat.rose::before  { background: linear-gradient(90deg, #E8D4D8, #C9A0A8); }
    .soft-stat.sage::before  { background: linear-gradient(90deg, #D4E5DA, #8FAF9B); }
    .soft-stat.sky::before   { background: linear-gradient(90deg, #D4E3ED, #7A9EB5); }
    .soft-stat.sand::before  { background: linear-gradient(90deg, #E8E0D4, #B5A68A); }
    .soft-stat.mauve::before { background: linear-gradient(90deg, #E5DFEC, #B8A9C9); }

    .soft-stat .ss-label {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 0.3rem;
    }

    .soft-stat .ss-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--text);
        line-height: 1.2;
    }

    .soft-stat .ss-hint {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.3rem;
    }

    /* KPI cards (white) */
    .kpi-card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: var(--shadow);
        height: 100%;
        border: 1px solid var(--border);
    }

    .kpi-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }

    .kpi-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text);
    }

    .kpi-delta { font-size: 0.76rem; margin-top: 0.25rem; }
    .kpi-delta.positive { color: #5A9A6E; }
    .kpi-delta.negative { color: #C47A7A; }
    .kpi-delta.neutral  { color: #94A3B8; }

    /* Panels */
    .panel {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
        overflow: hidden;
    }

    .panel-head {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #F1F5F9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .panel-head h3 {
        margin: 0;
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text);
    }

    .panel-head span {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    .panel-body {
        padding: 0.75rem 0.85rem 0.5rem;
    }

    .chart-card-wrap {
        background: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
        margin: 0;
    }

    .chart-card-title {
        display: none;
    }

    /* Chips / summary */
    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .chip {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.45rem 0.85rem;
        font-size: 0.8rem;
        color: var(--text-muted);
        box-shadow: var(--shadow);
    }

    .chip strong { color: var(--text); }

    .section-gap { height: 0.5rem; }

    /* Streamlit widgets */
    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.68rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text);
    }

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid var(--border);
        overflow: hidden;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #C9B8D4, #B8A9C9) !important;
        border-radius: 4px;
    }

    .stProgress > div > div > div {
        background: #F1F5F9 !important;
        border-radius: 4px;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #B8A9C9 0%, #9B8AA5 100%) !important;
        border: none !important;
        color: #fff !important;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(155, 138, 165, 0.25);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: transparent;
        border-bottom: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: var(--text-muted);
    }

    .stTabs [aria-selected="true"] {
        background: var(--accent-soft) !important;
        color: #6B5B7A !important;
    }

    h1, h2, h3 { color: var(--text); }

    hr { border: none; border-top: 1px solid var(--border); margin: 1.25rem 0; }
</style>
"""


def apply_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", delta_type: str = "neutral") -> str:
    delta_class = delta_type if delta_type in ("positive", "negative", "neutral") else "neutral"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def soft_stat_card(label: str, value: str, hint: str = "", variant: str = "mauve") -> str:
    v = variant if variant in ("rose", "sage", "sky", "sand", "mauve") else "mauve"
    hint_html = f'<div class="ss-hint">{hint}</div>' if hint else ""
    return f"""
    <div class="soft-stat {v}">
        <div class="ss-label">{label}</div>
        <div class="ss-value">{value}</div>
        {hint_html}
    </div>
    """


def gradient_kpi_card(label: str, value: str, sub: str = "", variant: str = "mauve") -> str:
    """Обратная совместимость — мягкие карточки вместо ярких градиентов."""
    return soft_stat_card(label, value, sub, variant)


def panel_start(title: str, subtitle: str = "") -> None:
    sub = f"<span>{subtitle}</span>" if subtitle else ""
    st.markdown(
        f'<div class="panel"><div class="panel-head"><h3>{title}</h3>{sub}</div><div class="panel-body">',
        unsafe_allow_html=True,
    )


def panel_end() -> None:
    st.markdown("</div></div>", unsafe_allow_html=True)


def chart_card_start(title: str) -> None:
    panel_start(title)


def chart_card_end() -> None:
    panel_end()


def chip_row(items: list[tuple[str, str]]) -> None:
    chips = "".join(f'<div class="chip"><strong>{k}:</strong> {v}</div>' for k, v in items)
    st.markdown(f'<div class="chip-row">{chips}</div>', unsafe_allow_html=True)


def apply_chart_style(fig, title: str | None = None, height: int = 340):
    layout_updates = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=36 if title else 16, b=8),
        height=height,
        font=dict(family="Inter, sans-serif", color="#64748B", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=11),
    )
    if title:
        layout_updates["title"] = dict(
            text=title,
            font=dict(size=14, color="#1E293B"),
            x=0,
            xanchor="left",
        )
    return fig.update_layout(**layout_updates)


def donut_chart(labels, values, title: str = "", height: int = 320):
    import plotly.graph_objects as go

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.58,
                marker=dict(colors=CHART_COLORS[: len(labels)], line=dict(color="#fff", width=1)),
                textinfo="percent",
                textfont=dict(size=10, color="#475569"),
                hovertemplate="%{label}<br>%{value:,.0f}<br>%{percent}<extra></extra>",
            )
        ]
    )
    return apply_chart_style(fig, title=title or None, height=height)


def bar_chart(x, y, title: str = "", color: str = PRIMARY_LIGHT, text=None, height: int = 320):
    import plotly.graph_objects as go

    fig = go.Figure(
        data=[
            go.Bar(
                x=x,
                y=y,
                marker=dict(color=color, line=dict(width=0)),
                text=text,
                textposition="outside",
                textfont=dict(color="#64748B", size=10),
            )
        ]
    )
    return apply_chart_style(fig, title=title or None, height=height)


def area_chart(x, y, title: str = "", color: str = PRIMARY_LIGHT, height: int = 320):
    import plotly.graph_objects as go

    r, g, b = _hex_to_rgb(color)
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line=dict(color=color, width=2.5, shape="spline"),
                fill="tozeroy",
                fillcolor=f"rgba({r},{g},{b},0.12)",
            )
        ]
    )
    return apply_chart_style(fig, title=title or None, height=height)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
