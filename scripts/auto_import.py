"""Скрипт для Планировщика заданий Windows: импорт файлов из data/inbox."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database import init_db, session_scope
from services.onec_import import scan_inbox


def main() -> None:
    init_db()
    with session_scope() as session:
        logs = [(log.status, log.message) for log in scan_inbox(session)]
    for status, message in logs:
        print(f"[{status}] {message}")


if __name__ == "__main__":
    main()
