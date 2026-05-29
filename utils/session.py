import streamlit as st

from config import load_onec_config
from database import session_scope
from services.auth_service import get_all_companies_tuples, get_user_companies_tuples
from services.onec_import import scan_inbox


def init_session_state() -> None:
    defaults = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "role": None,
        "last_auto_import": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def try_auto_import() -> None:
    """Автоимпорт файлов из data/inbox при включённой настройке."""
    config = load_onec_config()
    if not config.get("auto_import_enabled"):
        return
    try:
        with session_scope() as session:
            logs = scan_inbox(session)
            if logs:
                st.session_state.last_auto_import = logs[-1].message
    except Exception:
        pass


def require_login() -> bool:
    init_session_state()
    if not st.session_state.logged_in:
        st.switch_page("app.py")
        st.stop()
    try_auto_import()
    return True


def logout() -> None:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None


def current_user_is_admin() -> bool:
    return st.session_state.get("role") == "Admin"


def get_accessible_companies() -> list[tuple[int, str]]:
    """Список (id, name) — без привязки к сессии SQLAlchemy."""
    with session_scope() as session:
        if current_user_is_admin():
            return get_all_companies_tuples(session)
        return get_user_companies_tuples(session, st.session_state.user_id)


def company_selector(key: str = "company_id", label: str = "Компания") -> int:
    companies = get_accessible_companies()
    if not companies:
        st.info(
            "Нет данных. Загрузите демо-данные или импортируйте файлы из 1С "
            "(раздел «Импорт 1С»)."
        )
        st.stop()
    options = {name: cid for cid, name in companies}
    name = st.selectbox(label, list(options.keys()), key=f"{key}_name")
    return options[name]
