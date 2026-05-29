import hashlib

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from models import Company, User, UserCompany


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def login(session: Session, username: str, password: str) -> dict[str, int | str] | None:
    user = session.scalar(select(User).where(User.username == username))
    if user is None or user.password_hash != hash_password(password):
        return None
    return {"id": user.id, "username": user.username, "role": user.role}


def is_admin(user: User | None) -> bool:
    return user is not None and user.role == "Admin"


def get_user_companies(session: Session, user_id: int) -> list[Company]:
    links = session.scalars(
        select(UserCompany)
        .where(UserCompany.user_id == user_id)
        .options(joinedload(UserCompany.company))
    ).all()
    return [link.company for link in links]


def companies_as_tuples(companies: list[Company]) -> list[tuple[int, str]]:
    return [(c.id, c.name) for c in companies]


def get_user_companies_tuples(session: Session, user_id: int) -> list[tuple[int, str]]:
    return companies_as_tuples(get_user_companies(session, user_id))


def get_all_companies_tuples(session: Session) -> list[tuple[int, str]]:
    return companies_as_tuples(get_all_companies(session))


def register_user(
    session: Session,
    username: str,
    password: str,
    role: str,
    company_ids: list[int],
) -> User:
    user = User(username=username, password_hash=hash_password(password), role=role)
    session.add(user)
    session.flush()
    for company_id in company_ids:
        session.add(UserCompany(user_id=user.id, company_id=company_id))
    return user


def list_users(session: Session) -> list[User]:
    return list(session.scalars(select(User).order_by(User.username)).all())


def delete_user(session: Session, user_id: int) -> None:
    session.execute(delete(UserCompany).where(UserCompany.user_id == user_id))
    user = session.get(User, user_id)
    if user:
        session.delete(user)


def get_all_companies(session: Session) -> list[Company]:
    return list(session.scalars(select(Company).order_by(Company.name)).all())
