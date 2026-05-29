import streamlit as st
from sqlalchemy import select

from database import session_scope
from models import User
from services.auth_service import delete_user, get_all_companies_tuples, list_users, register_user
from utils.layout import setup_page
from utils.session import current_user_is_admin, require_login

require_login()
setup_page("Пользователи", "Управление доступом")

if not current_user_is_admin():
    st.error("Доступ только для администратора")
    st.stop()

with session_scope() as session:
    users = [(u.id, u.username, u.role) for u in list_users(session)]
    companies = get_all_companies_tuples(session)

for user_id, username, role in users:
    c1, c2, c3 = st.columns([3, 2, 1])
    c1.write(f"**{username}**")
    c2.write(role)
    if username != "admin" and c3.button("Удалить", key=f"del_{user_id}"):
        with session_scope() as s:
            delete_user(s, user_id)
        st.rerun()

st.divider()
with st.form("add_user"):
    new_username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")
    role = st.selectbox("Роль", ["Admin", "Manager"])
    company_names = [name for _, name in companies]
    selected = st.multiselect("Компании", company_names)
    if st.form_submit_button("Создать"):
        if new_username and password:
            ids = [cid for cid, name in companies if name in selected]
            with session_scope() as session:
                if session.scalar(select(User).where(User.username == new_username)):
                    st.error("Пользователь уже существует")
                else:
                    register_user(session, new_username, password, role, ids)
                    st.success("Создан")
                    st.rerun()
