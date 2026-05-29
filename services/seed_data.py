"""Демо-данные: компании с разным ФОТ и кадровым профилем."""

import random
from datetime import date, timedelta
from typing import Any, Dict, List

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models import (
    Absence,
    AbsenceType,
    Company,
    Employee,
    Overtime,
    SalaryHistory,
    User,
    UserCompany,
    WorkScheduleType,
)

# Базовые 4 + 5 новых компаний
COMPANIES = [
    {
        "name": "ООО ТехноСистемы",
        "industry": "IT",
        "size": "Средняя",
        "region": "Москва",
        "external_id": "tech-001",
    },
    {
        "name": "АО Производственные Решения",
        "industry": "Производство",
        "size": "Крупная",
        "region": "Санкт-Петербург",
        "external_id": "prod-001",
    },
    {
        "name": "ИП Розничная Сеть",
        "industry": "Розничная торговля",
        "size": "Малая",
        "region": "Новосибирск",
        "external_id": "retail-001",
    },
    {
        "name": "ООО Финансовые Технологии",
        "industry": "Финансы",
        "size": "Средняя",
        "region": "Москва",
        "external_id": "fintech-001",
    },
    {
        "name": "ООО СтройМонтаж",
        "industry": "Строительство",
        "size": "Средняя",
        "region": "Казань",
        "external_id": "build-001",
    },
    {
        "name": "ООО МедЦентр Плюс",
        "industry": "Здравоохранение",
        "size": "Средняя",
        "region": "Екатеринбург",
        "external_id": "med-001",
    },
    {
        "name": "АО Логистика Север",
        "industry": "Логистика",
        "size": "Крупная",
        "region": "Мурманск",
        "external_id": "log-001",
    },
    {
        "name": "ООО Образование XXI",
        "industry": "Образование",
        "size": "Малая",
        "region": "Нижний Новгород",
        "external_id": "edu-001",
    },
    {
        "name": "ИП АгроТех",
        "industry": "Сельское хозяйство",
        "size": "Малая",
        "region": "Краснодар",
        "external_id": "agro-001",
    },
]

# Профиль влияет на ФОТ, численность и текучесть
COMPANY_PROFILES: Dict[str, Dict[str, Any]] = {
    "tech-001": {"salary_mult": 1.45, "headcount": 10, "turnover": 0.12, "overtime_mult": 1.3},
    "prod-001": {"salary_mult": 1.05, "headcount": 14, "turnover": 0.18, "overtime_mult": 1.6},
    "retail-001": {"salary_mult": 0.82, "headcount": 6, "turnover": 0.28, "overtime_mult": 0.7},
    "fintech-001": {"salary_mult": 1.65, "headcount": 9, "turnover": 0.10, "overtime_mult": 1.1},
    "build-001": {"salary_mult": 0.98, "headcount": 16, "turnover": 0.30, "overtime_mult": 1.8},
    "med-001": {"salary_mult": 1.15, "headcount": 11, "turnover": 0.08, "overtime_mult": 0.9},
    "log-001": {"salary_mult": 0.92, "headcount": 13, "turnover": 0.22, "overtime_mult": 1.5},
    "edu-001": {"salary_mult": 0.75, "headcount": 5, "turnover": 0.14, "overtime_mult": 0.5},
    "agro-001": {"salary_mult": 0.88, "headcount": 7, "turnover": 0.20, "overtime_mult": 1.2},
}

NEW_COMPANY_IDS = {"build-001", "med-001", "log-001", "edu-001", "agro-001"}

DEPARTMENTS = [
    "Отдел IT",
    "Продажи",
    "Производство",
    "Бухгалтерия",
    "Юридический отдел",
    "HR",
    "Маркетинг",
    "Логистика",
    "Поддержка клиентов",
    "Разработка",
]

POSITIONS = [
    "Разработчик",
    "Менеджер по продажам",
    "Инженер",
    "Бухгалтер",
    "Юрист",
    "HR-менеджер",
    "Маркетолог",
    "Логист",
    "Специалист поддержки",
    "Аналитик",
    "Дизайнер",
    "Тестировщик",
    "Руководитель отдела",
    "Директор",
]

EDUCATION_LEVELS = [
    "Среднее",
    "Среднее специальное",
    "Высшее (бакалавр)",
    "Высшее (магистр)",
    "Кандидат наук",
    "Доктор наук",
]

NAMES = [
    "Иванов Иван Иванович",
    "Петров Петр Петрович",
    "Сидоров Сидр Сидорович",
    "Кузнецов Кузьма Кузьмич",
    "Смирнова Анна Сергеевна",
    "Козлова Мария Петровна",
    "Новиков Алексей Дмитриевич",
    "Морозов Денис Александрович",
    "Волкова Елена Игоревна",
    "Лебедев Олег Николаевич",
    "Соколов Игорь Викторович",
    "Попова Ольга Андреевна",
    "Васечкин Василий Васильевич",
    "Фёдоров Максим Олегович",
    "Михайлова Дарья Константиновна",
    "Алексеев Роман Сергеевич",
    "Егорова Ксения Павловна",
    "Корейба Егор Дмитриевич",
    "Никитин Артём Владимирович",
    "Орлова Татьяна Викторовна",
    "Григорьев Сергей Алексеевич",
    "Белова Ирина Олеговна",
    "Кириллов Андрей Николаевич",
    "Зайцева Марина Дмитриевна",
    "Семёнов Павел Игоревич",
    "Фомина Екатерина Сергеевна",
    "Гусев Владимир Петрович",
    "Титова Надежда Александровна",
    "Комаров Артём Владимирович",
    "Антонова Ольга Игоревна",
    "Романов Илья Павлович",
    "Степанова Виктория Андреевна",
    "Медведев Григорий Сергеевич",
    "Ковалёва Алина Дмитриевна",
    "Жуков Никита Олегович",
    "Соловьёва Юлия Игоревна",
    "Воробьёв Константин Алексеевич",
    "Павлова Светлана Викторовна",
    "Сергеев Дмитрий Николаевич",
    "Макарова Полина Сергеевна",
]


def _profile(external_id: str) -> Dict[str, Any]:
    return COMPANY_PROFILES.get(
        external_id,
        {"salary_mult": 1.0, "headcount": 6, "turnover": 0.2, "overtime_mult": 1.0},
    )


def _employee_name(company_idx: int, emp_idx: int) -> str:
    idx = (company_idx * 17 + emp_idx * 3) % len(NAMES)
    return NAMES[idx]


def _generate_employee(
    company_id: int,
    name: str,
    index: int,
    profile: Dict[str, Any],
) -> Employee:
    dept = DEPARTMENTS[index % len(DEPARTMENTS)]
    position = POSITIONS[index % len(POSITIONS)]
    schedule = random.choice(list(WorkScheduleType)).value

    work_hours = {
        WorkScheduleType.FULL_TIME.value: 40.0,
        WorkScheduleType.PART_TIME.value: 20.0,
        WorkScheduleType.SHIFT.value: 36.0,
        WorkScheduleType.FLEXIBLE.value: 30.0,
        WorkScheduleType.REMOTE.value: 40.0,
    }[schedule]

    hire_year = 2020 + (index % 5)
    hire_month = 1 + (index % 12)
    hire_day = 1 + (index % 28)

    termination_date = None
    if random.random() < profile["turnover"]:
        term_year = hire_year + random.randint(1, 3)
        term_month = random.randint(1, 12)
        term_day = random.randint(1, 28)
        termination_date = date(term_year, term_month, term_day)

    return Employee(
        external_id=f"emp-{company_id:03d}-{index + 1:03d}",
        name=name,
        department=dept,
        position=position,
        company_id=company_id,
        hire_date=date(hire_year, hire_month, hire_day),
        termination_date=termination_date,
        work_schedule=schedule,
        work_hours_per_week=work_hours,
        experience_years=random.randint(0, 20),
        education_level=random.choice(EDUCATION_LEVELS),
    )


def _generate_salary_history(
    employee: Employee,
    months: List[date],
    profile: Dict[str, Any],
) -> List[SalaryHistory]:
    salaries = []
    base_salary = round((45000 + (hash(employee.name) % 80000)) * profile["salary_mult"], 2)

    for idx, period in enumerate(months):
        if employee.termination_date and period > employee.termination_date.replace(day=1):
            break

        growth = 1 + idx * 0.02
        salary = round(base_salary * growth, 2)
        bonus = round(salary * (0.05 if idx % 3 else 0.15), 2) if idx >= 5 else 0
        vacation_pay = round(salary * 0.08, 2) if idx in (6, 11) else 0

        sick_leave_pay = 0
        if random.random() < 0.1:
            sick_leave_pay = round(salary * 0.7 * random.uniform(0.1, 0.3), 2)

        overtime_pay = 0
        ot_chance = 0.3 * profile["overtime_mult"]
        if employee.department in ["Производство", "IT", "Поддержка клиентов", "Логистика"]:
            if random.random() < min(ot_chance, 0.55):
                overtime_pay = round(salary / 22 * 1.5 * random.uniform(1, 5), 2)

        working_days = 22
        actual_worked_days = working_days - random.randint(0, 3)
        total_income = salary + bonus + vacation_pay + sick_leave_pay + overtime_pay
        ndfl = round(total_income * 0.13, 2)

        salaries.append(
            SalaryHistory(
                employee_id=employee.id,
                salary=salary,
                bonus=bonus,
                vacation_pay=vacation_pay,
                sick_leave_pay=sick_leave_pay,
                overtime_pay=overtime_pay,
                ndfl=ndfl,
                date=period,
                working_days=working_days,
                actual_worked_days=actual_worked_days,
            )
        )

    return salaries


def _generate_absences(employee: Employee, start_date: date, end_date: date) -> List[Absence]:
    absences = []

    if random.random() < 0.8:
        vacation_start = start_date + timedelta(days=random.randint(0, 200))
        vacation_days = random.randint(14, 28)
        vacation_end = vacation_start + timedelta(days=vacation_days)

        if vacation_end <= end_date:
            absences.append(
                Absence(
                    employee_id=employee.id,
                    absence_type=AbsenceType.VACATION,
                    start_date=vacation_start,
                    end_date=vacation_end,
                    days_count=vacation_days,
                    reason="Ежегодный оплачиваемый отпуск",
                    is_paid=True,
                )
            )

    for _ in range(random.randint(1, 3)):
        sick_start = start_date + timedelta(days=random.randint(0, 300))
        sick_days = random.randint(3, 14)
        sick_end = sick_start + timedelta(days=sick_days)

        if sick_end <= end_date:
            absences.append(
                Absence(
                    employee_id=employee.id,
                    absence_type=AbsenceType.SICK_LEAVE,
                    start_date=sick_start,
                    end_date=sick_end,
                    days_count=sick_days,
                    reason="Временная нетрудоспособность",
                    is_paid=True,
                )
            )

    return absences


def _generate_overtime(
    employee: Employee,
    start_date: date,
    end_date: date,
    profile: Dict[str, Any],
) -> List[Overtime]:
    overtimes = []
    base_prob = {
        "Производство": 0.4,
        "IT": 0.3,
        "Поддержка клиентов": 0.3,
        "Продажи": 0.2,
        "Маркетинг": 0.1,
        "Логистика": 0.35,
    }.get(employee.department, 0.1)
    overtime_probability = min(base_prob * profile["overtime_mult"], 0.65)

    current_date = start_date
    while current_date <= end_date:
        if random.random() < overtime_probability:
            hours = random.uniform(1, 4)
            coefficient = 1.5 if current_date.weekday() < 5 else 2.0
            overtimes.append(
                Overtime(
                    employee_id=employee.id,
                    date=current_date,
                    hours=hours,
                    coefficient=coefficient,
                    reason="Срочный проект" if random.random() < 0.5 else "Плановая переработка",
                    approved_by="Руководитель отдела",
                )
            )
        current_date += timedelta(days=random.randint(1, 7))

    return overtimes


def _months_range() -> tuple[List[date], date, date]:
    months: List[date] = []
    for y, m in [
        (2025, 5), (2025, 6), (2025, 7), (2025, 8), (2025, 9), (2025, 10),
        (2025, 11), (2025, 12), (2026, 1), (2026, 2), (2026, 3), (2026, 4),
    ]:
        months.append(date(y, m, 1))
    start_date = months[0]
    end_date = months[-1] + timedelta(days=30)
    return months, start_date, end_date


def _populate_company(
    session: Session,
    company: Company,
    company_idx: int,
    months: List[date],
    start_date: date,
    end_date: date,
    rng_seed: int,
) -> tuple[int, int, int, int]:
    random.seed(rng_seed + company_idx)
    profile = _profile(company.external_id)
    employees: List[Employee] = []
    salaries: List[SalaryHistory] = []
    absences: List[Absence] = []
    overtimes: List[Overtime] = []

    for idx in range(profile["headcount"]):
        name = _employee_name(company_idx, idx)
        employee = _generate_employee(company.id, name, idx, profile)
        employees.append(employee)

    session.add_all(employees)
    session.flush()

    for idx, employee in enumerate(employees):
        salaries.extend(_generate_salary_history(employee, months, profile))
        if not employee.termination_date or employee.termination_date > start_date:
            absences.extend(_generate_absences(employee, start_date, end_date))
            overtimes.extend(_generate_overtime(employee, start_date, end_date, profile))

    session.add_all(salaries)
    session.add_all(absences)
    session.add_all(overtimes)
    return len(employees), len(salaries), len(absences), len(overtimes)


def _link_admin_to_companies(session: Session, companies: List[Company]) -> None:
    admin = session.scalar(select(User).where(User.username == "admin"))
    if admin is None:
        return
    existing = {
        uc.company_id
        for uc in session.scalars(
            select(UserCompany).where(UserCompany.user_id == admin.id)
        ).all()
    }
    for company in companies:
        if company.id not in existing:
            session.add(UserCompany(user_id=admin.id, company_id=company.id))


def ensure_extended_companies(session: Session) -> int:
    """Добавить 5 новых компаний, если их ещё нет в БД."""
    added = 0
    months, start_date, end_date = _months_range()
    new_companies: List[Company] = []

    for company_idx, company_data in enumerate(COMPANIES):
        if company_data["external_id"] not in NEW_COMPANY_IDS:
            continue
        exists = session.scalar(
            select(Company).where(Company.external_id == company_data["external_id"])
        )
        if exists:
            continue
        company = Company(**company_data)
        session.add(company)
        session.flush()
        _populate_company(session, company, company_idx, months, start_date, end_date, 42)
        new_companies.append(company)
        added += 1

    if new_companies:
        _link_admin_to_companies(session, new_companies)
    return added


def add_test_data(session: Session) -> None:
    """Полная перезагрузка демо-данных (все компании)."""
    session.execute(delete(Overtime))
    session.execute(delete(Absence))
    session.execute(delete(SalaryHistory))
    session.execute(delete(Employee))
    session.execute(delete(UserCompany))
    session.execute(delete(Company))
    session.flush()

    companies: List[Company] = []
    for company_data in COMPANIES:
        company = Company(**company_data)
        session.add(company)
        companies.append(company)

    session.flush()

    months, start_date, end_date = _months_range()
    total_emp = total_sal = total_abs = total_ot = 0

    for company_idx, company in enumerate(companies):
        e, s, a, o = _populate_company(
            session, company, company_idx, months, start_date, end_date, 42
        )
        total_emp += e
        total_sal += s
        total_abs += a
        total_ot += o

    _link_admin_to_companies(session, companies)
    session.flush()

    print(
        f"Создано: {len(companies)} компаний, {total_emp} сотрудников, "
        f"{total_sal} записей зарплат, {total_abs} отсутствий, {total_ot} переработок"
    )
