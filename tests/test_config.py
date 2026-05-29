"""Тесты конфигурации."""

import json

from config import DEFAULT_ONEC_CONFIG, load_onec_config, save_onec_config


def test_load_onec_config_defaults(tmp_path, monkeypatch):
    import config as cfg

    data_dir = tmp_path / "data"
    monkeypatch.setattr(cfg, "DATA_DIR", data_dir)
    monkeypatch.setattr(cfg, "INBOX_DIR", data_dir / "inbox")
    monkeypatch.setattr(cfg, "PROCESSED_DIR", data_dir / "processed")
    monkeypatch.setattr(cfg, "TEMPLATES_DIR", data_dir / "templates")
    monkeypatch.setattr(cfg, "ONEC_CONFIG_PATH", data_dir / "onec_config.json")

    loaded = load_onec_config()
    assert loaded["auto_import_enabled"] is False
    assert loaded["odata_url"] == ""


def test_save_and_load_onec_config(tmp_path, monkeypatch):
    import config as cfg

    data_dir = tmp_path / "data"
    monkeypatch.setattr(cfg, "DATA_DIR", data_dir)
    monkeypatch.setattr(cfg, "INBOX_DIR", data_dir / "inbox")
    monkeypatch.setattr(cfg, "PROCESSED_DIR", data_dir / "processed")
    monkeypatch.setattr(cfg, "TEMPLATES_DIR", data_dir / "templates")
    cfg_path = data_dir / "onec_config.json"
    monkeypatch.setattr(cfg, "ONEC_CONFIG_PATH", cfg_path)

    save_onec_config({"odata_url": "http://1c.local/odata", "auto_import_enabled": True})
    loaded = load_onec_config()
    assert loaded["odata_url"] == "http://1c.local/odata"
    assert loaded["auto_import_enabled"] is True
    assert loaded["company_name"] == DEFAULT_ONEC_CONFIG["company_name"]

    raw = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert "odata_url" in raw
