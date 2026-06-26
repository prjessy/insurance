from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from kv.config import load_config


def doc_id_from_path(path: Path) -> str:
    h = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:12]
    return h


def slugify(text: str, max_len: int = 60) -> str:
    text = Path(text).stem
    text = re.sub(r"[^\w\s가-힣-]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text.strip())
    return (text or "untitled")[:max_len]


def build_tags(source_type: str, extra: list[str] | None = None) -> list[str]:
    cfg = load_config()
    tags = list(cfg.get("default_tags", ["수집/자동"]))
    tags.extend(cfg.get("source_tags", {}).get(source_type, []))
    if extra:
        tags.extend(extra)
    # 중복 제거, 순서 유지
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def make_frontmatter(
    *,
    title: str,
    source_type: str,
    source_file: Path,
    tags: list[str] | None = None,
    status: str = "raw",
    extra: dict | None = None,
) -> dict:
    fm = {
        "title": title,
        "tags": tags or build_tags(source_type),
        "source_type": source_type,
        "source_file": str(source_file.as_posix()),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "doc_id": doc_id_from_path(source_file),
        "status": status,
    }
    if extra:
        fm.update(extra)
    return fm


def render_markdown(frontmatter: dict, body: str) -> str:
    yaml_block = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    body = body.strip()
    return f"---\n{yaml_block}\n---\n\n{body}\n"


def parse_markdown(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        fm = {}
    body = parts[2].strip()
    return fm, body
