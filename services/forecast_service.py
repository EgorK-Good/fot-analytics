"""Прогноз ФОТ: Prophet с запасным трендовым методом и полным расчётом выплат."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from prophet import Prophet
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import Employee, SalaryHistory

logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)

MIN_PROPHET_MONTHS = 3
MIN_YEARLY_SEASONALITY = 24


def _fot_amount(row: SalaryHistory) -> float:
    return (
        float(row.salary)
        + float(row.bonus)
        + float(row.vacation_pay)
        + float(row.sick_leave_pay or 0)
        + float(row.overtime_pay or 0)
    )


def _monthly_fot_series(session: Session, company_id: int) -> pd.DataFrame:
    rows = session.scalars(
        select(SalaryHistory)
        .join(Employee)
        .where(Employee.company_id == company_id)
        .options(joinedload(SalaryHistory.employee))
        .order_by(SalaryHistory.date)
    ).all()
    if not rows:
        return pd.DataFrame(columns=["ds", "y"])

    df = pd.DataFrame([{"date": r.date, "fot": _fot_amount(r)} for r in rows])
    df["ds"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("ds", as_index=False)["fot"].sum()
    monthly = monthly.rename(columns={"fot": "y"})
    monthly = monthly.sort_values("ds").reset_index(drop=True)

    # Сглаживание выбросов (IQR) — одна аномальная выплата не ломает прогноз
    if len(monthly) >= 4:
        q1, q3 = monthly["y"].quantile(0.25), monthly["y"].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr if iqr > 0 else monthly["y"].max()
        monthly["y"] = monthly["y"].clip(upper=upper)

    return monthly


def _prophet_model(n_obs: int) -> Prophet:
    return Prophet(
        yearly_seasonality=n_obs >= MIN_YEARLY_SEASONALITY,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="additive",
        changepoint_prior_scale=0.04,
        seasonality_prior_scale=12,
        interval_width=0.85,
    )


def _trend_forecast(monthly: pd.DataFrame, periods: int) -> pd.DataFrame:
    """Линейный тренд по последним месяцам, если Prophet недоступен."""
    y = monthly["y"].astype(float)
    slope = (y.iloc[-1] - y.iloc[0]) / max(len(y) - 1, 1) if len(y) > 1 else 0.0
    last_ds = monthly["ds"].max()

    hist = monthly.copy()
    hist["type"] = "История"
    hist["actual"] = hist["y"]
    hist["yhat"] = hist["y"]
    hist["yhat_lower"] = hist["y"] * 0.92
    hist["yhat_upper"] = hist["y"] * 1.08

    val = float(y.iloc[-1])
    fut_rows = []
    for ds in pd.date_range(last_ds, periods=periods + 1, freq="MS")[1:]:
        val = max(0.0, val + slope)
        fut_rows.append(
            {
                "ds": ds,
                "yhat": val,
                "yhat_lower": val * 0.9,
                "yhat_upper": val * 1.1,
                "type": "Прогноз",
                "actual": np.nan,
            }
        )
    fut = pd.DataFrame(fut_rows)
    return pd.concat([hist.drop(columns=["y"], errors="ignore"), fut], ignore_index=True)


def _run_prophet(monthly: pd.DataFrame, periods: int) -> pd.DataFrame:
    train = monthly[["ds", "y"]].copy()
    model = _prophet_model(len(train))
    model.fit(train)
    future = model.make_future_dataframe(periods=periods, freq="MS")
    forecast = model.predict(future)
    last_hist = train["ds"].max()

    out = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    for col in ("yhat", "yhat_lower", "yhat_upper"):
        out[col] = out[col].clip(lower=0)

    out["type"] = out["ds"].apply(lambda d: "История" if d <= last_hist else "Прогноз")
    out = out.merge(train.rename(columns={"y": "actual"}), on="ds", how="left")
    return out


def predict_fot(
    session: Session, company_id: int, months_ahead: int = 1
) -> tuple[float, pd.DataFrame]:
    monthly = _monthly_fot_series(session, company_id)
    if monthly.empty:
        return 0.0, monthly
    if len(monthly) < MIN_PROPHET_MONTHS:
        result = _trend_forecast(monthly, months_ahead)
    else:
        try:
            result = _run_prophet(monthly, months_ahead)
        except Exception:
            result = _trend_forecast(monthly, months_ahead)

    last_hist = monthly["ds"].max()
    target = last_hist + pd.DateOffset(months=months_ahead)
    fut = result[(result["type"] == "Прогноз") & (result["ds"] == target)]
    if fut.empty:
        fut = result[result["type"] == "Прогноз"].tail(1)
    predicted = float(fut["yhat"].iloc[0]) if not fut.empty else 0.0
    return max(predicted, 0.0), result


def predict_fot_horizon(session: Session, company_id: int, months_ahead: int = 6) -> pd.DataFrame:
    """История + прогноз для графика (с доверительным интервалом)."""
    monthly = _monthly_fot_series(session, company_id)
    if len(monthly) < 2:
        return pd.DataFrame(
            columns=["ds", "yhat", "yhat_lower", "yhat_upper", "type", "actual"]
        )

    if len(monthly) < MIN_PROPHET_MONTHS:
        out = _trend_forecast(monthly, months_ahead)
    else:
        try:
            out = _run_prophet(monthly, months_ahead)
        except Exception:
            out = _trend_forecast(monthly, months_ahead)

    out["month_label"] = out["ds"].dt.strftime("%b %Y")
    return out


def forecast_summary_table(horizon_df: pd.DataFrame) -> pd.DataFrame:
    """Таблица прогнозных месяцев для UI."""
    fut = horizon_df[horizon_df["type"] == "Прогноз"].copy()
    if fut.empty:
        return fut
    return fut.assign(
        Период=fut["ds"].dt.strftime("%m.%Y"),
        Прогноз=fut["yhat"].round(0),
        Нижняя_граница=fut["yhat_lower"].round(0),
        Верхняя_граница=fut["yhat_upper"].round(0),
    )[["Период", "Прогноз", "Нижняя_граница", "Верхняя_граница"]]
