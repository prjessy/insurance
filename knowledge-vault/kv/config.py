from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml


def _roots() -> tuple[Path, Path]:
    """(데이터 루트, 번들 루트) 반환.

    - 개발 모드: 둘 다 knowledge-vault 폴더
    - exe(frozen) 모드: 데이터=exe 옆 폴더, 번들=_MEIPASS(읽기전용 리소스)
    """
    if getattr(sys, "frozen", False):
        app = Path(sys.executable).resolve().parent
        bundle = Path(getattr(sys, "_MEIPASS", app))
        return app, bundle
    pkg_parent = Path(__file__).resolve().parent.parent
    return pkg_parent, pkg_parent


ROOT, BUNDLE_DIR = _roots()
INBOX = ROOT / "inbox"
VAULT_RAW = ROOT / "vault" / "raw"
VAULT_REFINED = ROOT / "vault" / "refined"
INDEX_DIR = ROOT / "index"
CONFIG_PATH = ROOT / "config.yaml"


def _dir_with_fallback(name: str) -> Path:
    """exe 옆에 있으면 그걸, 없으면 번들의 기본본을 사용."""
    local = ROOT / name
    if local.exists():
        return local
    bundled = BUNDLE_DIR / name
    return bundled if bundled.exists() else local


PROFILES_DIR = _dir_with_fallback("profiles")


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def index_db_path() -> Path:
    cfg = load_config()
    rel = cfg.get("index_db", "index/search.db")
    return ROOT / rel


def resolve_vault_path(vault: str) -> Path:
    """obsidian_vault 값을 Path 로. 상대경로는 knowledge-vault(ROOT) 기준."""
    p = Path(vault).expanduser()
    if not p.is_absolute():
        p = ROOT / p
    return p.resolve()


# ---------------------------------------------------------------------------
# 산업 프로파일 (Industry Profile)
# ---------------------------------------------------------------------------
# "보험"에 박혀 있던 도메인 용어/폴더명을 프로파일로 추출.
# config.yaml 의 `profile:` 키로 전환한다.
#   profile: insurance        -> profiles/insurance.yaml 로드
#   profile: support          -> profiles/support.yaml 로드 (기술지원)
#   profile: {labels: {...}}  -> 인라인 정의
# 어떤 키든 비어 있으면 아래 DEFAULT_PROFILE 값으로 채워진다(하위호환).

DEFAULT_PROFILE: dict = {
    "name": "금융",
    "category": "금융",          # 금융 / 관리 / 기술 ...
    "labels": {
        "entity": "고객",          # 서비스 대상 (고객/티켓/회원/거래처)
        "catalog": "상품",         # 제공 항목 (상품/해결책/서비스)
        "record": "상담",          # 상호작용 1건 (상담/처리/미팅)
        "records": "상담기록",     # 상호작용 기록 모음
        "proposal": "제안서",      # 산출물 ②
        "message": "안내 문자",    # 산출물 ③
        "channel": "채널",
        "date": "상담일",
    },
    "folders": {
        "entity_db": "고객DB",
        "catalog_db": "상품DB",
        "records": "상담기록",
        "queue": "AI작업큐",
    },
    "record_tags": ["상담", "painpoint/녹취정리", "수집/자동"],
    # 프롬프트는 비워두면 vault 의 프롬프트.md 섹션(①②③④)으로 대체된다.
    "prompts": {},
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _load_profile_file(name: str) -> dict:
    pf = PROFILES_DIR / f"{name}.yaml"
    if pf.exists():
        with open(pf, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def load_profile() -> dict:
    """현재 활성 프로파일을 DEFAULT_PROFILE 위에 병합해 반환."""
    cfg = load_config()
    prof = cfg.get("profile")
    data: dict = {}
    if isinstance(prof, str) and prof.strip():
        data = _load_profile_file(prof.strip())
    elif isinstance(prof, dict):
        data = prof
    return _deep_merge(DEFAULT_PROFILE, data)


def profile_folder(key: str) -> str:
    """프로파일 폴더명 (entity_db/catalog_db/records/queue)."""
    folders = load_profile().get("folders", {})
    return folders.get(key) or DEFAULT_PROFILE["folders"].get(key, key)


def profile_label(key: str) -> str:
    """프로파일 표시 용어 (entity/catalog/record/proposal/message ...)."""
    labels = load_profile().get("labels", {})
    return labels.get(key) or DEFAULT_PROFILE["labels"].get(key, key)


def profile_prompt(key: str) -> str:
    """프로파일이 정의한 프롬프트. 없으면 빈 문자열(프롬프트.md 로 대체)."""
    prompts = load_profile().get("prompts", {})
    return (prompts.get(key) or "").strip()


def profile_record_tags() -> list[str]:
    return list(load_profile().get("record_tags", DEFAULT_PROFILE["record_tags"]))


def available_profiles() -> list[str]:
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in PROFILES_DIR.glob("*.yaml"))
