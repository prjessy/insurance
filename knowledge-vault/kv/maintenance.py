"""데이터 초기화(clean) — 변환·인덱스·작업큐를 비워 빈 상태로 되돌린다.

지우는 것: vault/raw, vault/refined, 검색 인덱스, processed 기록, AI작업큐
건드리지 않는 것: inbox 원본 파일, 고객DB·상품DB 등 참조 데이터 (옵션으로 포함 가능)
"""

from __future__ import annotations

import shutil

from kv.config import INDEX_DIR, VAULT_RAW, VAULT_REFINED, profile_folder
from kv.import_refs import vault_root


def clean(include_queue: bool = True, include_inbox: bool = False,
          include_refs: bool = False) -> dict:
    removed: list[str] = []

    def _rm(p):
        if p and p.exists():
            shutil.rmtree(p, ignore_errors=True)
            removed.append(str(p))

    # 변환물 + 인덱스 + processed 기록
    _rm(VAULT_RAW)
    _rm(VAULT_REFINED)
    _rm(INDEX_DIR)

    vr = vault_root()
    if include_queue and vr:
        _rm(vr / profile_folder("queue"))

    if include_inbox:
        from kv.config import INBOX
        for sub in ("audio", "images", "excel", "documents", "notes"):
            _rm(INBOX / sub)

    # 참조 데이터(고객DB·상품DB·기록) — 템플릿(_*.md)은 남김 → 대시보드 비움
    if include_refs and vr:
        for key in ("entity_db", "catalog_db", "records"):
            folder = vr / profile_folder(key)
            if folder.exists():
                for md in folder.glob("*.md"):
                    if not md.name.startswith("_"):
                        md.unlink()
                        removed.append(str(md))

    # 빈 폴더 복구
    for d in (VAULT_RAW, VAULT_REFINED, INDEX_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # 인덱스 비우기(재생성)
    try:
        from kv.search import rebuild_index
        rebuild_index()
    except Exception:
        pass

    return {"removed": removed}
