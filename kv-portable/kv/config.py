from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "inbox"
VAULT_RAW = ROOT / "vault" / "raw"
VAULT_REFINED = ROOT / "vault" / "refined"
INDEX_DIR = ROOT / "index"
CONFIG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def index_db_path() -> Path:
    cfg = load_config()
    rel = cfg.get("index_db", "index/search.db")
    return ROOT / rel
