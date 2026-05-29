from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from config import DATABASE_URL, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME
from models import Base, User
from services.auth_service import hash_password

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _migrate_columns() -> None:
    """Добавление новых колонок в существующую SQLite БД."""
    insp = inspect(engine)
    
    # Migrate salary_histories
    if insp.has_table("salary_histories"):
        cols = {c["name"] for c in insp.get_columns("salary_histories")}
        alters = []
        if "sick_leave_pay" not in cols:
            alters.append("ALTER TABLE salary_histories ADD COLUMN sick_leave_pay NUMERIC(18,2) DEFAULT 0")
        if "overtime_pay" not in cols:
            alters.append("ALTER TABLE salary_histories ADD COLUMN overtime_pay NUMERIC(18,2) DEFAULT 0")
        if "working_days" not in cols:
            alters.append("ALTER TABLE salary_histories ADD COLUMN working_days INTEGER DEFAULT 22")
        if "actual_worked_days" not in cols:
            alters.append("ALTER TABLE salary_histories ADD COLUMN actual_worked_days INTEGER DEFAULT 22")
        if alters:
            with engine.begin() as conn:
                for sql in alters:
                    conn.execute(text(sql))

    # Migrate companies
    if insp.has_table("companies"):
        ccols = {c["name"] for c in insp.get_columns("companies")}
        alters = []
        if "industry" not in ccols:
            alters.append("ALTER TABLE companies ADD COLUMN industry VARCHAR(100)")
        if "size" not in ccols:
            alters.append("ALTER TABLE companies ADD COLUMN size VARCHAR(50)")
        if "region" not in ccols:
            alters.append("ALTER TABLE companies ADD COLUMN region VARCHAR(100)")
        if alters:
            with engine.begin() as conn:
                for sql in alters:
                    conn.execute(text(sql))

    # Migrate employees
    if insp.has_table("employees"):
        ecols = {c["name"] for c in insp.get_columns("employees")}
        alters = []
        if "position" not in ecols:
            alters.append("ALTER TABLE employees ADD COLUMN position VARCHAR(100) DEFAULT ''")
        if "work_schedule" not in ecols:
            alters.append("ALTER TABLE employees ADD COLUMN work_schedule VARCHAR(20) DEFAULT 'FULL_TIME'")
        if "work_hours_per_week" not in ecols:
            alters.append("ALTER TABLE employees ADD COLUMN work_hours_per_week FLOAT DEFAULT 40.0")
        if "experience_years" not in ecols:
            alters.append("ALTER TABLE employees ADD COLUMN experience_years INTEGER")
        if "education_level" not in ecols:
            alters.append("ALTER TABLE employees ADD COLUMN education_level VARCHAR(50)")
        if alters:
            with engine.begin() as conn:
                for sql in alters:
                    conn.execute(text(sql))

    # Create new tables if they don't exist
    new_tables = ["absences", "overtimes"]
    for table in new_tables:
        if not insp.has_table(table):
            Base.metadata.tables[table].create(bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _migrate_columns()
    with session_scope() as session:
        admin = session.query(User).filter_by(username=DEFAULT_ADMIN_USERNAME).first()
        if admin is None:
            session.add(
                User(
                    username=DEFAULT_ADMIN_USERNAME,
                    password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                    role="Admin",
                )
            )
        from services.seed_data import ensure_extended_companies

        ensure_extended_companies(session)


@contextmanager
def session_scope():
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
