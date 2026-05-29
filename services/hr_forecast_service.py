"""Прогноз кадровых показателей с ограничениями и запасным трендом."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from prophet import Prophet
from sqlalchemy.orm import Session

from services.hr_analyzer import headcount_by_month, turnover_by_month

logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)

MIN_PROPHET_MONTHS = 3
MIN_YEARLY_SEASONALITY = 24


def _prophet_model(n_obs: int) -> Prophet:
    return Prophet(
        yearly_seasonality=n_obs >= MIN_YEARLY_SEASONALITY,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.03,
        seasonality_prior_scale=15,
        interval_width=0.85,
    )


def _trend_forecast(series: pd.DataFrame, value_col: str, months_ahead: int) -> pd.DataFrame:
    train = series[["ds", value_col]].copy()
    y = train[value_col].astype(float)
    slope = (y.iloc[-1] - y.iloc[0]) / max(len(y) - 1, 1) if len(y) > 1 else 0.0
    last_ds = train["ds"].max()

    hist = train.rename(columns={value_col: "actual"})
    hist["type"] = "История"
    hist["yhat"] = hist["actual"]
    hist["yhat_lower"] = hist["actual"]
    hist["yhat_upper"] = hist["actual"]

    val = float(y.iloc[-1])
    fut_rows = []
    for ds in pd.date_range(last_ds, periods=months_ahead + 1, freq="MS")[1:]:
        val = val + slope
        fut_rows.append(
            {
                "ds": ds,
                "yhat": val,
                "yhat_lower": val,
                "yhat_upper": val,
                "type": "Прогноз",
                "actual": np.nan,
            }
        )
    return pd.concat([hist, pd.DataFrame(fut_rows)], ignore_index=True)


def _postprocess(series_kind: str, df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    for col in ("yhat", "yhat_lower", "yhat_upper"):
        if col not in df.columns:
            continue
        if series_kind == "headcount":
            df[col] = df[col].clip(lower=0)
        elif series_kind == "turnover_pct":
            df[col] = df[col].clip(lower=0, upper=100)
    if series_kind == "headcount" and "yhat" in df.columns:
        df["yhat"] = df["yhat"].round().astype(int)
    elif series_kind == "turnover_pct" and "yhat" in df.columns:
        df["yhat"] = df["yhat"].round(2)
    return df


def _prophet_forecast(
    series: pd.DataFrame, value_col: str, months_ahead: int, series_kind: str
) -> pd.DataFrame:
    if series.empty or len(series) < 2:
        return pd.DataFrame()

    train = series.rename(columns={value_col: "y"})[["ds", "y"]].copy()
    train["y"] = train["y"].astype(float)

    if len(train) < MIN_PROPHET_MONTHS:
        out = _trend_forecast(series, value_col, months_ahead)
        return _postprocess(series_kind, out)

    try:
        model = _prophet_model(len(train))
        model.fit(train)
        future = model.make_future_dataframe(periods=months_ahead, freq="MS")
        forecast = model.predict(future)
        last_hist = train["ds"].max()
        out = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        out["type"] = out["ds"].apply(lambda d: "История" if d <= last_hist else "Прогноз")
        out = out.merge(train.rename(columns={"y": "actual"}), on="ds", how="left")
    except Exception:
        out = _trend_forecast(series, value_col, months_ahead)

    return _postprocess(series_kind, out)


def forecast_headcount(session: Session, company_id: int, months_ahead: int = 6) -> pd.DataFrame:
    series = headcount_by_month(session, company_id, months=36)
    return _prophet_forecast(series, "headcount", months_ahead, "headcount")


def forecast_turnover(session: Session, company_id: int, months_ahead: int = 6) -> pd.DataFrame:
    series = turnover_by_month(session, company_id, months=36)
    return _prophet_forecast(series, "turnover_pct", months_ahead, "turnover_pct")
