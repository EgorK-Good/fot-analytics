import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'fot_analytics.db'}"

DATA_DIR = BASE_DIR / "data"
INBOX_DIR = DATA_DIR / "inbox"
PROCESSED_DIR = DATA_DIR / "processed"
TEMPLATES_DIR = DATA_DIR / "templates"
ONEC_CONFIG_PATH = DATA_DIR / "onec_config.json"

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"

DEFAULT_ONEC_CONFIG = {
    "odata_url": "",
    "odata_user": "",
    "odata_password": "",
    "auto_import_enabled": False,
    "auto_import_interval_minutes": 60,
    "company_name": "Организация из 1С",
}


def ensure_dirs() -> None:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


def load_onec_config() -> dict:
    ensure_dirs()
    if ONEC_CONFIG_PATH.exists():
        return {**DEFAULT_ONEC_CONFIG, **json.loads(ONEC_CONFIG_PATH.read_text(encoding="utf-8"))}
    return DEFAULT_ONEC_CONFIG.copy()


def save_onec_config(config: dict) -> None:
    ensure_dirs()
    ONEC_CONFIG_PATH.write_text(
        json.dumps({**DEFAULT_ONEC_CONFIG, **config}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
