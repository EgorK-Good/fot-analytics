"""Тесты генерации отчётов Excel."""

from datetime import date
from io import BytesIO

import pandas as pd

from services.report_service import generate_fot_report


def test_generate_fot_report(session, company, salary_records):
    data = generate_fot_report(
        session,
        company.id,
        date(2025, 1, 1),
        date(2026, 12, 31),
    )
    assert len(data) > 0
    xls = pd.ExcelFile(BytesIO(data))
    assert "ФОТ по отделам" in xls.sheet_names
    assert "Динамика зарплат" in xls.sheet_names
    assert "Текучесть кадров" in xls.sheet_names
    assert "Соотношение окладов и премий" in xls.sheet_names


def test_generate_fot_report_empty(session, company):
    data = generate_fot_report(
        session,
        company.id,
        date(2020, 1, 1),
        date(2020, 12, 31),
    )
    assert len(data) > 0
    xls = pd.ExcelFile(BytesIO(data))
    df = pd.read_excel(xls, "ФОТ по отделам")
    assert df.empty or len(df) == 0
