"""Импорт данных из 1С: файлы (CSV/Excel) и OData REST API."""

from __future__ import annotations

import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import INBOX_DIR, PROCESSED_DIR, load_onec_config
from models import Company, Employee, ImportLog, SalaryHistory

# Сопоставление типичных колонок выгрузки 1С
EMPLOYEE_COLUMNS = {
    "external_id": ["ref", "guid", "id", "код", "идентификатор", "external_id"],
    "name": ["name", "фио", "сотрудник", "фамилияимяотчество", "employee"],
    "department": ["department", "подразделение", "отдел", "департамент"],
    "hire_date": ["hire_date", "датаприема", "принят", "датаприема"],
    "termination_date": ["termination_date", "датаувольнения", "уволен", "датаувольнения"],
    "company": ["company", "организация", "company_name"],
}

ACCRUAL_COLUMNS = {
    "external_id": ["employee_ref", "ref", "guid", "сотрудник", "кодсотрудника", "employee_id"],
    "period": ["period", "период", "месяц", "date", "дата"],
    "salary": ["salary", "оклад", "начислено", "зарплата", "salary_amount"],
    "bonus": ["bonus", "премия", "премии", "bonus_amount"],
    "vacation_pay": ["vacation_pay", "отпускные", "отпуск", "vacation"],
    "ndfl": ["ndfl", "ндфл", "налог", "tax"],
}


def _normalize(name: str) -> str:
    return "".join(ch for ch in name.lower().strip() if ch.isalnum())


def _map_columns(df: pd.DataFrame, mapping: dict[str, list[str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    normalized = {_normalize(c): c for c in df.columns}
    for target, aliases in mapping.items():
        for alias in aliases:
            key = _normalize(alias)
            if key in normalized:
                result[target] = normalized[key]
                break
    return result


def _parse_date(value: Any) -> date | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, date):
        return value
    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _read_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")


def _get_or_create_company(session: Session, name: str, external_id: str | None = None) -> Company:
    if external_id:
        company = session.scalar(select(Company).where(Company.external_id == external_id))
        if company:
            return company
    company = session.scalar(select(Company).where(Company.name == name))
    if company:
        return company
    company = Company(name=name, external_id=external_id)
    session.add(company)
    session.flush()
    return company


def import_employees_df(session: Session, df: pd.DataFrame, default_company: str) -> int:
    cols = _map_columns(df, EMPLOYEE_COLUMNS)
    if "name" not in cols:
        raise ValueError("Не найдена колонка с ФИО сотрудника")

    count = 0
    for _, row in df.iterrows():
        ext_id = str(row[cols["external_id"]]) if "external_id" in cols and pd.notna(row[cols["external_id"]]) else None
        company_name = str(row[cols["company"]]) if "company" in cols and pd.notna(row[cols["company"]]) else default_company
        company = _get_or_create_company(session, company_name, ext_id)

        employee = None
        if ext_id:
            employee = session.scalar(
                select(Employee).where(Employee.external_id == ext_id, Employee.company_id == company.id)
            )
        if employee is None:
            employee = Employee(
                external_id=ext_id,
                name=str(row[cols["name"]]).strip(),
                department=str(row[cols.get("department", cols["name"])]).strip()
                if "department" in cols
                else "Не указан",
                company_id=company.id,
                hire_date=_parse_date(row[cols["hire_date"]]) if "hire_date" in cols else date.today(),
                termination_date=_parse_date(row[cols["termination_date"]])
                if "termination_date" in cols
                else None,
            )
            session.add(employee)
        else:
            employee.name = str(row[cols["name"]]).strip()
            if "department" in cols:
                employee.department = str(row[cols["department"]]).strip()
            if "hire_date" in cols:
                employee.hire_date = _parse_date(row[cols["hire_date"]]) or employee.hire_date
            if "termination_date" in cols:
                employee.termination_date = _parse_date(row[cols["termination_date"]])
        count += 1
    session.flush()
    return count


def import_accruals_df(session: Session, df: pd.DataFrame) -> int:
    cols = _map_columns(df, ACCRUAL_COLUMNS)
    if "period" not in cols:
        raise ValueError("Не найдена колонка периода начисления")

    count = 0
    for _, row in df.iterrows():
        ext_id = str(row[cols["external_id"]]) if "external_id" in cols else None
        if not ext_id:
            continue
        employee = session.scalar(select(Employee).where(Employee.external_id == ext_id))
        if not employee:
            continue

        period = _parse_date(row[cols["period"]])
        if not period:
            continue
        period = period.replace(day=1)

        salary = float(row[cols["salary"]]) if "salary" in cols and pd.notna(row[cols["salary"]]) else 0.0
        bonus = float(row[cols["bonus"]]) if "bonus" in cols and pd.notna(row[cols["bonus"]]) else 0.0
        vacation = (
            float(row[cols["vacation_pay"]])
            if "vacation_pay" in cols and pd.notna(row[cols["vacation_pay"]])
            else 0.0
        )
        ndfl = float(row[cols["ndfl"]]) if "ndfl" in cols and pd.notna(row[cols["ndfl"]]) else salary * 0.13

        existing = session.scalar(
            select(SalaryHistory).where(
                SalaryHistory.employee_id == employee.id,
                SalaryHistory.date == period,
            )
        )
        if existing:
            existing.salary = salary
            existing.bonus = bonus
            existing.vacation_pay = vacation
            existing.ndfl = ndfl
        else:
            session.add(
                SalaryHistory(
                    employee_id=employee.id,
                    salary=salary,
                    bonus=bonus,
                    vacation_pay=vacation,
                    ndfl=ndfl,
                    date=period,
                )
            )
        count += 1
    session.flush()
    return count


def import_file(session: Session, path: Path, source: str = "file") -> ImportLog:
    config = load_onec_config()
    try:
        df = _read_file(path)
        name_lower = path.stem.lower()
        if "начисл" in name_lower or "accrual" in name_lower or "salary" in name_lower:
            count = import_accruals_df(session, df)
            msg = f"Импортировано начислений: {count}"
        elif "сотрудник" in name_lower or "employee" in name_lower or "кадр" in name_lower:
            count = import_employees_df(session, df, config["company_name"])
            msg = f"Импортировано сотрудников: {count}"
        else:
            # Пробуем определить по колонкам
            cols = _map_columns(df, ACCRUAL_COLUMNS)
            if "period" in cols:
                count = import_accruals_df(session, df)
                msg = f"Импортировано начислений: {count}"
            else:
                count = import_employees_df(session, df, config["company_name"])
                msg = f"Импортировано сотрудников: {count}"

        log = ImportLog(source=source, status="ok", message=msg, records_count=count)
        session.add(log)
        session.flush()
        return log
    except Exception as exc:
        log = ImportLog(source=source, status="error", message=str(exc), records_count=0)
        session.add(log)
        session.flush()
        raise


def import_from_upload(session: Session, file_bytes: bytes, filename: str) -> ImportLog:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    path = INBOX_DIR / filename
    path.write_bytes(file_bytes)
    log = import_file(session, path, source="upload")
    shutil.move(str(path), str(PROCESSED_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{filename}"))
    return log


def scan_inbox(session: Session) -> list[ImportLog]:
    """Автоимпорт: обработка всех файлов из папки inbox."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    logs: list[ImportLog] = []
    for path in sorted(INBOX_DIR.glob("*")):
        if path.suffix.lower() not in {".csv", ".xlsx", ".xls"}:
            continue
        try:
            log = import_file(session, path, source="auto")
            shutil.move(str(path), str(PROCESSED_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{path.name}"))
            logs.append(log)
        except Exception:
            continue
    return logs


def import_from_odata(session: Session) -> ImportLog:
    """Загрузка через OData (типовой REST API публикации 1С)."""
    config = load_onec_config()
    url = (config.get("odata_url") or "").strip().rstrip("/")
    if not url:
        raise ValueError("Укажите URL OData в настройках импорта 1С")

    auth = None
    if config.get("odata_user"):
        auth = (config["odata_user"], config.get("odata_password", ""))

    employees_url = f"{url}/Catalog_Сотрудники?$format=json"
    accruals_url = f"{url}/Document_НачислениеЗарплаты?$format=json"

    total = 0
    try:
        resp = requests.get(employees_url, auth=auth, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("value", data) if isinstance(data, dict) else data
        if rows:
            df = pd.DataFrame(rows)
            rename = {
                "Ref_Key": "external_id",
                "Description": "name",
                "Подразделение_Key": "department",
            }
            df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
            total += import_employees_df(session, df, config["company_name"])
    except requests.RequestException:
        pass

    try:
        resp = requests.get(accruals_url, auth=auth, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("value", data) if isinstance(data, dict) else data
        if rows:
            df = pd.DataFrame(rows)
            total += import_accruals_df(session, df)
    except requests.RequestException:
        pass

    if total == 0:
        raise ValueError(
            "OData не вернул данных. Проверьте URL и имена сущностей в вашей публикации 1С."
        )

    log = ImportLog(
        source="odata",
        status="ok",
        message=f"Импортировано записей через OData: {total}",
        records_count=total,
    )
    session.add(log)
    session.flush()
    return log
