from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class WorkScheduleType(str, Enum):
    FULL_TIME = "full_time"  # Полный день
    PART_TIME = "part_time"  # Неполный день
    SHIFT = "shift"  # Сменный график
    FLEXIBLE = "flexible"  # Гибкий график
    REMOTE = "remote"  # Удалённая работа


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Отрасль
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Размер компании
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Регион

    employees: Mapped[list["Employee"]] = relationship(back_populates="company")
    user_companies: Mapped[list["UserCompany"]] = relationship(back_populates="company")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)  # Должность
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    work_schedule: Mapped[WorkScheduleType] = mapped_column(
        SQLEnum(WorkScheduleType), default=WorkScheduleType.FULL_TIME
    )
    work_hours_per_week: Mapped[float] = mapped_column(Float, default=40.0)  # Часов в неделю
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Опыт работы (лет)
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Уровень образования

    company: Mapped["Company"] = relationship(back_populates="employees")
    salary_histories: Mapped[list["SalaryHistory"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    absences: Mapped[list["Absence"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    overtime_records: Mapped[list["Overtime"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class SalaryHistory(Base):
    __tablename__ = "salary_histories"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    salary: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    bonus: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    vacation_pay: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    sick_leave_pay: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)  # Больничные
    overtime_pay: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)  # Переработки
    ndfl: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    working_days: Mapped[int] = mapped_column(Integer, default=22)  # Рабочих дней в месяце
    actual_worked_days: Mapped[int] = mapped_column(Integer, default=22)  # Фактически отработано

    employee: Mapped["Employee"] = relationship(back_populates="salary_histories")

    @property
    def fot(self) -> float:
        return float(self.salary) + float(self.bonus) + float(self.vacation_pay) + float(self.sick_leave_pay) + float(self.overtime_pay)


class AbsenceType(str, Enum):
    VACATION = "vacation"  # Отпуск
    SICK_LEAVE = "sick_leave"  # Больничный
    UNPAID_LEAVE = "unpaid_leave"  # Отпуск без содержания
    BUSINESS_TRIP = "business_trip"  # Командировка
    OTHER = "other"  # Прочее


class Absence(Base):
    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    absence_type: Mapped[AbsenceType] = mapped_column(SQLEnum(AbsenceType), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_paid: Mapped[bool] = mapped_column(default=True)  # Оплачиваемый ли
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship(back_populates="absences")


class Overtime(Base):
    __tablename__ = "overtimes"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[float] = mapped_column(Float, nullable=False)  # Часы переработки
    coefficient: Mapped[float] = mapped_column(Float, default=1.5)  # Коэффициент оплаты
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship(back_populates="overtime_records")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    user_companies: Mapped[list["UserCompany"]] = relationship(back_populates="user")


class UserCompany(Base):
    __tablename__ = "user_companies"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="user_companies")
    company: Mapped["Company"] = relationship(back_populates="user_companies")


class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    records_count: Mapped[int] = mapped_column(default=0)
