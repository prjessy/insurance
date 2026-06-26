from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from kv.config import INBOX, ROOT, VAULT_RAW
from kv.converters import converter_for
from kv.tags import make_frontmatter, render_markdown, slugify


PROCESSED_LOG = ROOT / "index" / "processed.json"


def _load_processed() -> set[str]:
    if not PROCESSED_LOG.exists():
        return set()
    data = json.loads(PROCESSED_LOG.read_text(encoding="utf-8"))
    return set(data.get("files", []))


def _save_processed(keys: set[str]) -> None:
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_LOG.write_text(
        json.dumps({"files": sorted(keys)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def collect_inbox(force: bool = False) -> list[Path]:
    """inbox 하위 파일을 MD로 변환해 vault/raw 에 저장."""
    processed = set() if force else _load_processed()
    created: list[Path] = []

    for path in sorted(INBOX.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue

        key = str(path.resolve())
        if key in processed and not force:
            continue

        conv = converter_for(path, INBOX)
        if not conv:
            continue

        result = conv.convert(path)
        date_prefix = datetime.now().strftime("%Y-%m-%d")
        slug = slugify(path.name)
        out_name = f"{date_prefix}_{result.source_type}_{slug}.md"
        out_path = VAULT_RAW / out_name

        fm = make_frontmatter(
            title=result.title,
            source_type=result.source_type,
            source_file=path.relative_to(ROOT),
            extra=result.extra_meta,
        )
        out_path.write_text(render_markdown(fm, result.body), encoding="utf-8")
        created.append(out_path)
        processed.add(key)

    _save_processed(processed)
    return created


def inbox_status() -> dict:
    counts: dict[str, int] = {}
    for folder in INBOX.iterdir():
        if folder.is_dir():
            counts[folder.name] = sum(1 for f in folder.rglob("*") if f.is_file())
    raw_count = sum(1 for f in VAULT_RAW.glob("*.md"))
    return {"inbox": counts, "vault_raw": raw_count}
