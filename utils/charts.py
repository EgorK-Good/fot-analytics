"""Понятные графики для аналитики и прогнозов."""

from __future__ import annotations

from typing import Callable

import pandas as pd
import plotly.graph_objects as go

from utils.theme import PRIMARY_LIGHT, ROSE, apply_chart_style


def _month_tickformat():
    return "%b\n%Y"


def _add_forecast_divider(fig: go.Figure, last_hist_ts) -> None:
    if last_hist_ts is None or pd.isna(last_hist_ts):
        return
    fig.add_shape(
        type="line",
        x0=last_hist_ts,
        x1=last_hist_ts,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#94A3B8", width=1, dash="dot"),
    )
    fig.add_annotation(
        x=last_hist_ts,
        y=1,
        yref="paper",
        text="начало прогноза",
        showarrow=False,
        yanchor="bottom",
        font=dict(size=10, color="#64748B"),
    )


def forecast_line_chart(
    df: pd.DataFrame,
    *,
    y_format: Callable[[float], str] | None = None,
    value_name: str = "Значение",
    height: int = 400,
) -> go.Figure:
    """
    df: колонки ds, type, actual, yhat, yhat_lower, yhat_upper
    """
    fig = go.Figure()
    if df.empty:
        return apply_chart_style(fig, title="Нет данных", height=height)

    hist = df[df["type"] == "История"].copy()
    fut = df[df["type"] == "Прогноз"].copy()
    last_hist = hist["ds"].max() if not hist.empty else None

    if not fut.empty and "yhat_lower" in fut.columns and "yhat_upper" in fut.columns:
        fig.add_trace(
            go.Scatter(
                x=pd.concat([fut["ds"], fut["ds"].iloc[::-1]]),
                y=pd.concat([fut["yhat_upper"], fut["yhat_lower"].iloc[::-1]]),
                fill="toself",
                fillcolor="rgba(184, 169, 201, 0.2)",
                line=dict(width=0),
                name="Диапазон 85%",
                hoverinfo="skip",
                showlegend=True,
            )
        )

    if not hist.empty and hist["actual"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=hist["ds"],
                y=hist["actual"],
                mode="lines+markers",
                name="Факт",
                line=dict(color=PRIMARY_LIGHT, width=2.5),
                marker=dict(size=6, color=PRIMARY_LIGHT),
                hovertemplate="%{x|%B %Y}<br>Факт: %{y:,.0f}<extra></extra>",
            )
        )

    if not fut.empty:
        fig.add_trace(
            go.Scatter(
                x=fut["ds"],
                y=fut["yhat"],
                mode="lines+markers",
                name="Прогноз",
                line=dict(color=ROSE, width=2, dash="dash"),
                marker=dict(size=5, symbol="diamond", color=ROSE),
                hovertemplate="%{x|%B %Y}<br>Прогноз: %{y:,.0f}<extra></extra>",
            )
        )

    _add_forecast_divider(fig, last_hist)
    apply_chart_style(fig, height=height)
    fig.update_layout(
        xaxis=dict(tickformat=_month_tickformat()),
        yaxis_title=value_name,
        legend=dict(title=""),
        hovermode="x unified",
    )
    if y_format:
        fig.update_layout(yaxis_tickformat="~s")
    return fig


def fot_forecast_chart(df: pd.DataFrame, height: int = 420) -> go.Figure:
    fig = forecast_line_chart(df, value_name="ФОТ, ₽", height=height)
    fig.update_layout(yaxis_tickformat=",.0f")
    return fig


def headcount_forecast_chart(df: pd.DataFrame, height: int = 360) -> go.Figure:
    fig = forecast_line_chart(df, value_name="Человек", height=height)
    fig.update_layout(yaxis_tickformat="d")
    return fig


def turnover_forecast_chart(df: pd.DataFrame, height: int = 360) -> go.Figure:
    fig = forecast_line_chart(df, value_name="Текучесть, %", height=height)
    fig.update_layout(yaxis_tickformat=".1f", yaxis_range=[0, min(100, df["yhat"].max() * 1.2 + 5) if not df.empty else 100])
    return fig


def horizontal_bar(labels: list, values: list, title: str, color: str = PRIMARY_LIGHT, height: int = 320) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=color,
            text=[f"{v:,.0f}" if isinstance(v, (int, float)) else v for v in values],
            textposition="outside",
        )
    )
    apply_chart_style(fig, title=title, height=height)
    fig.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=120))
    return fig
