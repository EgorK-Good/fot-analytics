#!/usr/bin/env python
"""Скрипт для инициализации базы данных с расширенными данными."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import init_db, session_scope
from services.seed_data import add_test_data

def main():
    """Инициализировать БД с расширенными данными."""
    print("Инициализация базы данных...")
    
    # Инициализировать структуру БД
    init_db()
    
    # Добавить расширенные тестовые данные
    with session_scope() as session:
        add_test_data(session)
    
    print("✅ База данных успешно инициализирована с расширенными данными!")
    print(f"📊 Создано: 4 компании, ~30 сотрудников с расширенными атрибутами")
    print(f"📅 Данные за период: май 2025 - апрель 2026")
    print(f"📈 Включает: отпуска, больничные, переработки, разные графики работы")
    print("\nЗапустите приложение: streamlit run app.py")
    print("Доступно по адресу: http://localhost:8501")
    print("Логин/пароль: admin / admin")

if __name__ == "__main__":
    main()