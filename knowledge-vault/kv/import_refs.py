"""E:\\project\\work05 Obsidian 볼트 내 참조 문서 인덱싱."""

from __future__ import annotations

import re
from pathlib import Path

from kv.config import load_config, profile_folder, resolve_vault_path
from kv.tags import parse_markdown


def vault_root() -> Path | None:
    cfg = load_config()
    vault = (cfg.get("obsidian_vault") or "").strip()
    if not vault:
        return None
    return resolve_vault_path(vault)


def _excluded(name: str) -> bool:
    cfg = load_config()
    return name in set(cfg.get("exclude_dirs", []))


def iter_reference_files() -> list[tuple[Path, str, list[str]]]:
    """
    (파일경로, source_type, 추가태그) 목록 반환.
    source_type: reference/고객DB, reference/상품DB 등
    """
    root = vault_root()
    if not root:
        return []

    cfg = load_config()
    default_refs = [
        profile_folder("entity_db"),
        profile_folder("catalog_db"),
        profile_folder("records"),
    ]
    paths = cfg.get("reference_paths") or default_refs
    out: list[tuple[Path, str, list[str]]] = []

    for rel in paths:
        folder = root / rel
        if not folder.exists():
            continue
        tag_folder = rel.replace("\\", "/")
        for md in sorted(folder.rglob("*.md")):
            if md.name.startswith("_"):
                continue
            if any(_excluded(p.name) for p in md.parents):
                continue
            out.append((md, f"reference/{tag_folder}", [f"참조/{tag_folder}", "참조/볼트"]))

    # 루트 참조 md (README, 프롬프트, 대시보드 등)
    for md in sorted(root.glob("*.md")):
        out.append((md, "reference/root", ["참조/루트", "참조/볼트"]))

    return out


def doc_from_reference(path: Path, source_type: str, extra_tags: list[str]) -> dict:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_markdown(text)
    title = fm.get("title", path.stem)
    tags = list(fm.get("tags", [])) if isinstance(fm.get("tags"), list) else []
    for t in extra_tags:
        if t not in tags:
            tags.append(t)
    keywords = fm.get("keywords", [])
    if not keywords:
        words = re.findall(r"[가-힣]{2,}|[A-Za-z]{3,}", body)
        keywords = list(dict.fromkeys(words))[:12]
    return {
        "path": str(path),
        "title": title,
        "body": body if body else text,
        "tags": ",".join(tags),
        "keywords": ",".join(keywords) if isinstance(keywords, list) else str(keywords),
        "source_type": source_type,
    }


def count_references() -> dict[str, int]:
    counts: dict[str, int] = {}
    for path, stype, _ in iter_reference_files():
        key = stype.replace("reference/", "")
        counts[key] = counts.get(key, 0) + 1
    return counts
