import streamlit as st

from config import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, ensure_dirs
from database import init_db, session_scope
from services.auth_service import login
from utils.pages_routing import HOME
from utils.session import init_session_state, try_auto_import
from utils.theme import apply_theme

st.set_page_config(
    page_title="Клиент+",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
init_db()
init_session_state()
apply_theme()


def show_login() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(145deg, #E8E4EC 0%, #DDE6EF 50%, #E5DFEC 100%) !important;
        }
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        section.main > div {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 100dvh !important;
            padding: 1rem !important;
        }
        .main .block-container {
            max-width: 400px !important;
            width: 100% !important;
            padding: 2rem 2.25rem 1.5rem !important;
            margin: 0 auto !important;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(15, 23, 42, 0.12);
        }
        .main .block-container [data-testid="stVerticalBlock"] {
            gap: 0.35rem;
        }
        .login-title {
            text-align: center;
            margin: 0 0 0.25rem 0;
            font-size: 1.85rem;
            font-weight: 700;
            background: linear-gradient(135deg, #9B8AA5 0%, #8E7C9E 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .login-subtitle {
            text-align: center;
            color: #9CA3AF;
            font-size: 0.9rem;
            margin: 0 0 1.25rem 0;
        }
        .login-hint {
            text-align: center;
            color: #94A3B8;
            font-size: 0.78rem;
            margin-top: 0.75rem;
        }
        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }
        </style>
        <h1 class="login-title">Клиент+</h1>
        <p class="login-subtitle">Вход в систему</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input(
            "Логин",
            value=DEFAULT_ADMIN_USERNAME,
            label_visibility="visible",
            placeholder="Введите логин",
        )
        password = st.text_input(
            "Пароль",
            type="password",
            value=DEFAULT_ADMIN_PASSWORD,
            label_visibility="visible",
            placeholder="Введите пароль",
        )
        submitted = st.form_submit_button("Войти", use_container_width=True, type="primary")

        if submitted:
            with session_scope() as session:
                user = login(session, username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                try_auto_import()
                st.switch_page(HOME)
            else:
                st.error("Неверный логин или пароль")

    st.markdown(
        f'<p class="login-hint">По умолчанию: {DEFAULT_ADMIN_USERNAME} / {DEFAULT_ADMIN_PASSWORD}</p>',
        unsafe_allow_html=True,
    )


if not st.session_state.logged_in:
    show_login()
else:
    st.switch_page(HOME)
