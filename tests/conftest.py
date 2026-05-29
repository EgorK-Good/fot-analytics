"""Общие фикстуры: in-memory SQLite и тестовые данные."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Company, Employee, SalaryHistory, User, UserCompany, WorkScheduleType
from services.auth_service import hash_password


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine) -> Session:
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture
def company(session: Session) -> Company:
    org = Company(
        name="Тестовая организация",
        external_id="test-co-001",
        industry="IT",
        size="Малая",
        region="Москва",
    )
    session.add(org)
    session.flush()
    return org


@pytest.fixture
def second_company(session: Session) -> Company:
    org = Company(name="Вторая организация", external_id="test-co-002")
    session.add(org)
    session.flush()
    return org


@pytest.fixture
def employee(session: Session, company: Company) -> Employee:
    emp = Employee(
        external_id="emp-001",
        name="Иванов Иван Иванович",
        department="Отдел IT",
        position="Разработчик",
        company_id=company.id,
        hire_date=date(2024, 1, 15),
        termination_date=None,
        work_schedule=WorkScheduleType.FULL_TIME,
        work_hours_per_week=40.0,
    )
    session.add(emp)
    session.flush()
    return emp


@pytest.fixture
def terminated_employee(session: Session, company: Company) -> Employee:
    emp = Employee(
        external_id="emp-002",
        name="Петров Петр Петрович",
        department="Продажи",
        position="Менеджер",
        company_id=company.id,
        hire_date=date(2023, 6, 1),
        termination_date=date(2025, 3, 10),
        work_schedule=WorkScheduleType.FULL_TIME,
        work_hours_per_week=40.0,
    )
    session.add(emp)
    session.flush()
    return emp


@pytest.fixture
def salary_records(session: Session, employee: Employee) -> list[SalaryHistory]:
    records = [
        SalaryHistory(
            employee_id=employee.id,
            salary=100_000,
            bonus=10_000,
            vacation_pay=0,
            sick_leave_pay=0,
            overtime_pay=5_000,
            ndfl=14_950,
            date=date(2025, 12, 1),
        ),
        SalaryHistory(
            employee_id=employee.id,
            salary=105_000,
            bonus=15_000,
            vacation_pay=8_000,
            sick_leave_pay=0,
            overtime_pay=0,
            ndfl=16_640,
            date=date(2026, 1, 1),
        ),
        SalaryHistory(
            employee_id=employee.id,
            salary=105_000,
            bonus=20_000,
            vacation_pay=0,
            sick_leave_pay=3_000,
            overtime_pay=2_000,
            ndfl=16_900,
            date=date(2026, 2, 1),
        ),
    ]
    session.add_all(records)
    session.flush()
    return records


@pytest.fixture
def admin_user(session: Session, company: Company) -> User:
    user = User(
        username="testadmin",
        password_hash=hash_password("secret"),
        role="Admin",
    )
    session.add(user)
    session.flush()
    session.add(UserCompany(user_id=user.id, company_id=company.id))
    session.flush()
    return user


@pytest.fixture
def regular_user(session: Session, company: Company) -> User:
    user = User(
        username="testuser",
        password_hash=hash_password("userpass"),
        role="User",
    )
    session.add(user)
    session.flush()
    session.add(UserCompany(user_id=user.id, company_id=company.id))
    session.flush()
    return user
