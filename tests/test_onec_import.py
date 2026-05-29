"""Тесты сопоставления колонок импорта 1С."""

import pandas as pd

from services.onec_import import ACCRUAL_COLUMNS, EMPLOYEE_COLUMNS, _map_columns, _normalize


def test_normalize_strips_and_lowercases():
    assert _normalize("  ФИО  ") == "фио"
    assert _normalize("Hire_Date") == "hiredate"


def test_map_columns_russian_headers():
    df = pd.DataFrame(
        {
            "ФИО": ["Иванов"],
            "Подразделение": ["IT"],
            "Дата приема": ["01.01.2024"],
        }
    )
    mapped = _map_columns(df, EMPLOYEE_COLUMNS)
    assert mapped["name"] == "ФИО"
    assert mapped["department"] == "Подразделение"
    assert mapped["hire_date"] == "Дата приема"


def test_map_columns_english_headers():
    df = pd.DataFrame(
        {
            "employee_id": ["guid-1"],
            "salary": [1000],
            "bonus": [100],
            "period": ["2026-01-01"],
        }
    )
    mapped = _map_columns(df, ACCRUAL_COLUMNS)
    assert mapped["external_id"] == "employee_id"
    assert mapped["salary"] == "salary"
    assert mapped["period"] == "period"


def test_map_columns_partial():
    df = pd.DataFrame({"name": ["A"]})
    mapped = _map_columns(df, EMPLOYEE_COLUMNS)
    assert mapped["name"] == "name"
    assert "department" not in mapped
