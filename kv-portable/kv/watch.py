"""inbox 폴더 감시 → 자동 수집·정제·Obsidian 동기화."""

from __future__ import annotations

import time
from pathlib import Path

from kv.config import INBOX, load_config
from kv.ingest import collect_inbox
from kv.obsidian_sync import sync_to_obsidian
from kv.refine import refine_all
from kv.search import rebuild_index


def run_pipeline(force: bool = False) -> dict:
    created = collect_inbox(force=force)
    refined = refine_all(force=force)
    n = rebuild_index()
    sync_result = {"synced": 0, "skipped": 0, "dest": None}
    cfg = load_config()
    if cfg.get("obsidian_sync_auto", True):
        sync_result = sync_to_obsidian(force=force)
    return {
        "collected": len(created),
        "refined": len(refined),
        "indexed": n,
        "sync": sync_result,
    }


def watch_inbox() -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as e:
        raise SystemExit("watchdog 미설치: pip install watchdog") from e

    cfg = load_config()
    debounce = float(cfg.get("watch_debounce_sec", 3))
    pending: dict[str, float] = {}

    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            pending[event.src_path] = time.time()

        def on_modified(self, event):
            if event.is_directory:
                return
            pending[event.src_path] = time.time()

    observer = Observer()
    for folder in INBOX.iterdir():
        if folder.is_dir():
            observer.schedule(Handler(), str(folder), recursive=True)

    observer.start()
    print(f"inbox 감시 중... ({INBOX})")
    print("새 파일 → 자동 collect + refine + Obsidian sync")
    print("종료: Ctrl+C")

    try:
        while True:
            time.sleep(1)
            now = time.time()
            ready = [p for p, t in list(pending.items()) if now - t >= debounce]
            if ready:
                pending.clear()
                print(f"\n[{time.strftime('%H:%M:%S')}] {len(ready)}개 파일 감지 -> 파이프라인 실행")
                r = run_pipeline(force=False)
                print(f"  수집 {r['collected']} / 정제 {r['refined']} / 인덱스 {r['indexed']}")
                if r["sync"].get("dest"):
                    print(f"  Obsidian: {r['sync']['synced']}개 -> {r['sync']['dest']}")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
