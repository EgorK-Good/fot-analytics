from datetime import date
from io import BytesIO

import pandas as pd
from sqlalchemy.orm import Session

from services import fot_analyzer


def generate_fot_report(
    session: Session,
    company_id: int,
    start_date: date,
    end_date: date,
) -> bytes:
    fot_by_department = fot_analyzer.calculate_fot_by_department(
        session, company_id, start_date, end_date
    )
    salary_trend = fot_analyzer.calculate_salary_trend(session, company_id, start_date.year)
    turnover = fot_analyzer.calculate_turnover(session, company_id, start_date, end_date)
    ratio = fot_analyzer.calculate_salary_bonus_ratio(session, company_id, start_date, end_date)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(
            [{"Отдел": k, "ФОТ (руб)": v} for k, v in fot_by_department.items()]
        ).to_excel(writer, sheet_name="ФОТ по отделам", index=False)

        pd.DataFrame(
            [{"Месяц": k, "ФОТ (руб)": v} for k, v in salary_trend.items()]
        ).to_excel(writer, sheet_name="Динамика зарплат", index=False)

        pd.DataFrame(
            [{"Месяц": k, "Количество увольнений": v} for k, v in turnover.items()]
        ).to_excel(writer, sheet_name="Текучесть кадров", index=False)

        pd.DataFrame(
            [{"Тип": k, "Сумма (руб)": v} for k, v in ratio.items()]
        ).to_excel(writer, sheet_name="Соотношение окладов и премий", index=False)

    buffer.seek(0)
    return buffer.getvalue()
