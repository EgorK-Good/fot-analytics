"""Тесты аутентификации и управления пользователями."""

from services.auth_service import (
    companies_as_tuples,
    delete_user,
    get_all_companies_tuples,
    get_user_companies,
    get_user_companies_tuples,
    hash_password,
    is_admin,
    login,
    register_user,
)


def test_hash_password_deterministic():
    assert hash_password("admin") == hash_password("admin")
    assert hash_password("admin") != hash_password("other")


def test_login_success(session, admin_user):
    result = login(session, "testadmin", "secret")
    assert result is not None
    assert result["username"] == "testadmin"
    assert result["role"] == "Admin"
    assert result["id"] == admin_user.id


def test_login_wrong_password(session, admin_user):
    assert login(session, "testadmin", "wrong") is None


def test_login_unknown_user(session):
    assert login(session, "nobody", "secret") is None


def test_is_admin(admin_user, regular_user):
    assert is_admin(admin_user) is True
    assert is_admin(regular_user) is False
    assert is_admin(None) is False


def test_get_user_companies(session, regular_user, company, second_company):
    companies = get_user_companies(session, regular_user.id)
    assert len(companies) == 1
    assert companies[0].id == company.id

    tuples = get_user_companies_tuples(session, regular_user.id)
    assert tuples == [(company.id, company.name)]


def test_register_user_with_companies(session, company, second_company):
    user = register_user(
        session,
        username="newbie",
        password="pass123",
        role="User",
        company_ids=[company.id, second_company.id],
    )
    session.flush()
    assert user.id is not None
    links = get_user_companies(session, user.id)
    assert len(links) == 2


def test_companies_as_tuples(company):
    assert companies_as_tuples([company]) == [(company.id, company.name)]


def test_get_all_companies_tuples(session, company, second_company):
    all_cos = get_all_companies_tuples(session)
    names = {name for _, name in all_cos}
    assert company.name in names
    assert second_company.name in names


def test_delete_user(session, regular_user):
    uid = regular_user.id
    delete_user(session, uid)
    session.flush()
    assert login(session, "testuser", "userpass") is None
