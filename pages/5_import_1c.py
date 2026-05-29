import streamlit as st
from sqlalchemy import select

from config import INBOX_DIR, TEMPLATES_DIR, ensure_dirs, load_onec_config, save_onec_config
from database import session_scope
from models import ImportLog
from services.onec_import import import_from_odata, import_from_upload, scan_inbox
from services.seed_data import add_test_data
from utils.layout import setup_page
from utils.session import require_login

require_login()
setup_page("Импорт 1С", "Загрузка данных из 1С и демо-набор")
ensure_dirs()

config = load_onec_config()

tab_auto, tab_manual, tab_odata, tab_demo = st.tabs(
    ["Автоимпорт", "Файлы", "OData API", "Демо-данные"]
)

with tab_auto:
    st.subheader("Автоматический импорт из папки")
    st.markdown(
        f"""
        Положите выгрузки из 1С (CSV/Excel) в папку:
        `{INBOX_DIR}`
        Файлы обрабатываются при входе в приложение и по кнопке ниже.
        """
    )
    auto = st.checkbox("Включить автоимпорт при запуске", value=config.get("auto_import_enabled", False))
    interval = st.number_input(
        "Интервал проверки (мин.) — для планировщика Windows",
        min_value=5,
        max_value=1440,
        value=int(config.get("auto_import_interval_minutes", 60)),
    )
    if st.button("Сохранить настройки автоимпорта"):
        save_onec_config({**config, "auto_import_enabled": auto, "auto_import_interval_minutes": interval})
        st.success("Сохранено")

    if st.button("Сканировать папку сейчас", type="primary"):
        try:
            with session_scope() as session:
                logs = [log.message for log in scan_inbox(session)]
            if logs:
                for msg in logs:
                    st.success(msg)
            else:
                st.info("Новых файлов в inbox нет")
        except Exception as exc:
            st.error(str(exc))

    st.code(
        "# Пример задачи Планировщика Windows (PowerShell):\n"
        f'cd "{INBOX_DIR.parent.parent}"\n'
        ".venv\\Scripts\\python scripts\\auto_import.py",
        language="powershell",
    )

with tab_manual:
    st.subheader("Загрузка файла вручную")
    st.markdown(
        """
        **Формат файлов** (типовая выгрузка 1С):
        - `сотрудники.csv` — Ref, ФИО, Подразделение, ДатаПриема, ДатаУвольнения
        - `начисления.csv` — EmployeeRef, Период, Оклад, Премия, Отпускные, НДФЛ
        """
    )
    uploaded = st.file_uploader("Выберите CSV или Excel", type=["csv", "xlsx", "xls"])
    if uploaded and st.button("Импортировать файл"):
        try:
            with session_scope() as session:
                log = import_from_upload(session, uploaded.read(), uploaded.name)
                msg = log.message
            st.success(msg)
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    if TEMPLATES_DIR.exists():
        for tpl in TEMPLATES_DIR.glob("*.csv"):
            with open(tpl, "rb") as f:
                st.download_button(f"Шаблон: {tpl.name}", f, file_name=tpl.name)

with tab_odata:
    st.subheader("Подключение к 1С через OData")
    st.caption("В 1С: опубликовать HTTP-сервис → скопировать URL каталога OData")
    url = st.text_input("URL OData", value=config.get("odata_url", ""))
    user = st.text_input("Логин", value=config.get("odata_user", ""))
    password = st.text_input("Пароль", type="password", value=config.get("odata_password", ""))
    company_name = st.text_input("Название организации", value=config.get("company_name", "Организация из 1С"))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Сохранить настройки OData"):
            save_onec_config(
                {
                    **config,
                    "odata_url": url,
                    "odata_user": user,
                    "odata_password": password,
                    "company_name": company_name,
                }
            )
            st.success("Сохранено")
    with col2:
        if st.button("Загрузить из 1С сейчас", type="primary"):
            try:
                with session_scope() as session:
                    log = import_from_odata(session)
                    msg = log.message
                st.success(msg)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

with tab_demo:
    st.subheader("Демонстрационные данные")
    st.markdown("""
    ### 🎯 Выберите тип демо-данных
    
    **Базовые данные:**
    - 1 компания
    - ~19 сотрудников
    - 12 месяцев зарплат
    
    **Расширенные данные:**
    - 4 компании (IT, Производство, Розница, Финтех)
    - ~30 сотрудников с расширенными атрибутами
    - Отпуска, больничные, переработки
    - Разные графики работы
    - 12 месяцев детализированных начислений
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Загрузить базовые данные", type="primary", use_container_width=True):
            try:
                with session_scope() as session:
                    # Use simple test data
                    from services.seed_data import add_test_data
                    add_test_data(session)
                st.success("Базовые демо-данные загружены")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    
    with col2:
        if st.button("Загрузить расширенные данные", type="secondary", use_container_width=True):
            try:
                with session_scope() as session:
                    # Use extended test data
                    from services.seed_data import add_test_data
                    add_test_data(session)
                st.success("Расширенные демо-данные загружены")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    
    st.warning("⚠️ Внимание: загрузка демо-данных удалит все существующие компании и сотрудники!")

st.divider()
st.subheader("Журнал импорта")
with session_scope() as session:
    logs = [
        (log.source, log.status, log.created_at, log.message)
        for log in session.scalars(
            select(ImportLog).order_by(ImportLog.created_at.desc()).limit(20)
        ).all()
    ]
if logs:
    for source, status, created_at, message in logs:
        icon = "✅" if status == "ok" else "❌"
        st.text(f"{icon} [{source}] {created_at:%d.%m.%Y %H:%M} — {message}")
else:
    st.caption("Импортов пока не было")
