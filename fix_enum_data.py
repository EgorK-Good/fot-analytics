#!/usr/bin/env python
"""Скрипт для исправления данных Enum в базе данных."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from database import engine

def fix_enum_data():
    """Исправить значения Enum в базе данных."""
    print("Исправление данных Enum в базе данных...")
    
    with engine.begin() as conn:
        # Проверить, есть ли таблица employees
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"))
        if not result.fetchone():
            print("Таблица employees не найдена")
            return
        
        # Проверить, есть ли колонка work_schedule
        result = conn.execute(text("PRAGMA table_info(employees)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'work_schedule' not in columns:
            print("Колонка work_schedule не найдена")
            return
        
        # Обновить значения work_schedule
        update_mapping = {
            'full_time': 'FULL_TIME',
            'part_time': 'PART_TIME',
            'shift': 'SHIFT',
            'flexible': 'FLEXIBLE',
            'remote': 'REMOTE'
        }
        
        for old_value, new_value in update_mapping.items():
            result = conn.execute(
                text("UPDATE employees SET work_schedule = :new WHERE work_schedule = :old"),
                {"old": old_value, "new": new_value}
            )
            if result.rowcount > 0:
                print(f"Обновлено {result.rowcount} записей: {old_value} -> {new_value}")
        
        # Обновить значения absence_type в таблице absences
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='absences'"))
        if result.fetchone():
            absence_mapping = {
                'vacation': 'VACATION',
                'sick_leave': 'SICK_LEAVE',
                'unpaid_leave': 'UNPAID_LEAVE',
                'business_trip': 'BUSINESS_TRIP',
                'other': 'OTHER'
            }
            
            for old_value, new_value in absence_mapping.items():
                result = conn.execute(
                    text("UPDATE absences SET absence_type = :new WHERE absence_type = :old"),
                    {"old": old_value, "new": new_value}
                )
                if result.rowcount > 0:
                    print(f"Обновлено {result.rowcount} записей absences: {old_value} -> {new_value}")
    
    print("✅ Данные Enum успешно исправлены!")

if __name__ == "__main__":
    fix_enum_data()