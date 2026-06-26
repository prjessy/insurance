"""Obsidian vault 자동 동기화."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from kv.config import INBOX, ROOT, VAULT_REFINED, load_config
from kv.tags import parse_markdown

SYNC_LOG = ROOT / "index" / "obsidian_sync.json"


def obsidian_dest_for(source_type: str) -> Path | None:
    cfg = load_config()
    vault = (cfg.get("obsidian_vault") or "").strip()
    if not vault:
        return None
    routes = cfg.get("obsidian_routes") or {}
    sub = routes.get(source_type) or routes.get("default") or cfg.get("obsidian_subfolder", "KnowledgeVault")
    return Path(vault).expanduser().resolve() / str(sub).strip("/\\")


def obsidian_dest_root() -> Path | None:
    return obsidian_dest_for("default") or obsidian_dest_for("notes")


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_sync_log() -> dict:
    if SYNC_LOG.exists():
        return json.loads(SYNC_LOG.read_text(encoding="utf-8"))
    return {"files": {}, "attachments": {}}


def _save_sync_log(data: dict) -> None:
    SYNC_LOG.parent.mkdir(parents=True, exist_ok=True)
    data["last_sync"] = datetime.now(timezone.utc).isoformat()
    SYNC_LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _copy_attachment(source_rel: Path, dest_attach_dir: Path, log: dict) -> str | None:
    src = ROOT / source_rel
    if not src.exists() or not src.is_file():
        return None
    dest_attach_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_attach_dir / src.name
    key = str(source_rel.as_posix())
    h = _file_hash(src)
    if log.get("attachments", {}).get(key) == h and dest.exists():
        return dest.name
    shutil.copy2(src, dest)
    log.setdefault("attachments", {})[key] = h
    return dest.name


def sync_to_obsidian(force: bool = False) -> dict:
    """
    vault/refined MD -> Obsidian vault (유형별 폴더 라우팅).
    audio -> 상담기록, 기타 -> KnowledgeVault 등
    """
    cfg = load_config()
    vault = (cfg.get("obsidian_vault") or "").strip()
    if not vault:
        return {
            "synced": 0,
            "skipped": 0,
            "errors": ["obsidian_vault 경로가 config.yaml에 설정되지 않았습니다."],
            "dest": None,
        }

    copy_attach = cfg.get("obsidian_copy_attachments", True)
    log = _load_sync_log()
    synced = 0
    skipped = 0
    errors: list[str] = []
    dests_used: set[str] = set()

    for md_path in sorted(VAULT_REFINED.glob("*.md")):
        try:
            h = _file_hash(md_path)
            name = md_path.name
            log_key = f"{name}:{h}"
            if not force and log.get("files", {}).get(log_key):
                skipped += 1
                continue

            text = md_path.read_text(encoding="utf-8")
            fm, body = parse_markdown(text)
            source_type = fm.get("source_type", "notes")
            dest_root = obsidian_dest_for(source_type)
            if not dest_root:
                errors.append(f"{name}: 대상 폴더 없음")
                continue

            dest_root.mkdir(parents=True, exist_ok=True)
            dests_used.add(str(dest_root))
            attach_dir = dest_root / "attachments"

            if copy_attach:
                source_file = fm.get("source_file", "")
                if source_file:
                    att_name = _copy_attachment(Path(source_file), attach_dir, log)
                    if att_name:
                        fm["obsidian_attachment"] = f"attachments/{att_name}"

            out_text = _render_with_frontmatter(fm, body)
            (dest_root / name).write_text(out_text, encoding="utf-8")
            log.setdefault("files", {})[log_key] = h
            synced += 1
        except Exception as e:
            errors.append(f"{md_path.name}: {e}")

    for dest in dests_used:
        _update_index_note(Path(dest), synced, skipped)

    _save_sync_log(log)

    return {
        "synced": synced,
        "skipped": skipped,
        "errors": errors,
        "dest": ", ".join(sorted(dests_used)) if dests_used else str(obsidian_dest_root()),
    }


def _render_with_frontmatter(fm: dict, body: str) -> str:
    yaml_block = yaml.dump(fm, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{yaml_block}\n---\n\n{body.strip()}\n"


def _update_index_note(dest_root: Path, synced: int, skipped: int) -> None:
    """Obsidian MOC(목차) 노트 갱신."""
    index_path = dest_root / "_KnowledgeVault_목차.md"
    files = sorted(p.name for p in dest_root.glob("*.md") if not p.name.startswith("_"))
    lines = [
        "---",
        "tags:",
        "  - 수집/자동",
        "  - 상태/목차",
        f"updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "---",
        "",
        "# Knowledge Vault 목차",
        "",
        f"- 마지막 동기화: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- 이번 동기화: {synced}개 추가/갱신, {skipped}개 건너뜀",
        "",
        "## 문서 목록",
        "",
    ]
    for name in files:
        title = name.replace(".md", "")
        lines.append(f"- [[{title}]]")
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_status() -> dict:
    dest = obsidian_dest_root()
    log = _load_sync_log()
    return {
        "configured": dest is not None,
        "dest": str(dest) if dest else None,
        "last_sync": log.get("last_sync"),
        "synced_files": len(log.get("files", {})),
        "attachments": len(log.get("attachments", {})),
    }
