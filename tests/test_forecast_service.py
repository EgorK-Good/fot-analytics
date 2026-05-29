"""Тесты прогнозирования ФОТ (без тяжёлого Prophet)."""

import pandas as pd

from services.forecast_service import (
    _trend_forecast,
    forecast_summary_table,
    predict_fot,
    predict_fot_horizon,
)


def _sample_monthly() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ds": pd.to_datetime(["2025-10-01", "2025-11-01", "2025-12-01", "2026-01-01"]),
            "y": [100_000.0, 105_000.0, 110_000.0, 115_000.0],
        }
    )


def test_trend_forecast_structure():
    result = _trend_forecast(_sample_monthly(), periods=3)
    assert "type" in result.columns
    assert "yhat" in result.columns
    forecast_rows = result[result["type"] == "Прогноз"]
    assert len(forecast_rows) == 3
    assert forecast_rows["yhat"].min() >= 0


def test_forecast_summary_table():
    horizon = _trend_forecast(_sample_monthly(), periods=2)
    table = forecast_summary_table(horizon)
    assert len(table) == 2
    assert list(table.columns) == ["Период", "Прогноз", "Нижняя_граница", "Верхняя_граница"]


def test_forecast_summary_table_empty():
    empty = pd.DataFrame(columns=["ds", "yhat", "yhat_lower", "yhat_upper", "type"])
    assert forecast_summary_table(empty).empty


def test_predict_fot_empty(session, company):
    value, df = predict_fot(session, company.id, months_ahead=1)
    assert value == 0.0
    assert df.empty


def test_predict_fot_horizon_with_data(session, company, salary_records):
    horizon = predict_fot_horizon(session, company.id, months_ahead=2)
    assert not horizon.empty
    assert "Прогноз" in horizon["type"].values
