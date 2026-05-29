"""Пути к страницам (ASCII-имена файлов для совместимости со Streamlit на Windows)."""

from pathlib import Path

_PAGES_DIR = Path(__file__).resolve().parent.parent / "pages"

HOME = "pages/1_home.py"
EMPLOYEES = "pages/2_employees.py"
PAYROLL = "pages/3_payroll.py"
ANALYTICS = "pages/4_analytics.py"
IMPORT_1C = "pages/5_import_1c.py"
REPORTS = "pages/6_reports.py"
USERS = "pages/7_users.py"

NAV_ITEMS: list[tuple[str, str]] = [
    (HOME, "Главная"),
    (EMPLOYEES, "Сотрудники"),
    (PAYROLL, "Начисления"),
    (ANALYTICS, "Аналитика"),
    (IMPORT_1C, "Импорт 1С"),
    (REPORTS, "Отчёты"),
    (USERS, "Пользователи"),
]


def page_path(filename: str) -> str:
    return f"pages/{filename}"


def ensure_pages_exist() -> None:
    """Проверка, что файлы страниц на месте."""
    for rel in (HOME, EMPLOYEES, PAYROLL, ANALYTICS, IMPORT_1C, REPORTS, USERS):
        if not (_PAGES_DIR.parent / rel).is_file():
            raise FileNotFoundError(f"Не найдена страница: {rel}")
