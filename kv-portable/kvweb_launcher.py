"""배포(exe)용 런처 — 더블클릭하면 웹 UI가 브라우저로 열린다.

- CLI 아님: 사용자는 브라우저 화면만 본다.
- 데이터(config.yaml·고객DB·inbox·vault)는 exe 가 있는 폴더에 만들어진다.
- LLM 키는 exe 옆 key.txt 에서 읽는다 (각자 준비).
- 표준 라이브러리 웹서버(kv.webserver) 사용 → 가벼움. Whisper 미포함.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _setup() -> None:
    from kv.config import BUNDLE_DIR, ROOT

    # 첫 실행: 기본 config.yaml 을 exe 옆에 생성
    cfg = ROOT / "config.yaml"
    if not cfg.exists():
        for src in (BUNDLE_DIR / "config.portable.yaml", BUNDLE_DIR / "config.yaml"):
            if src.exists():
                shutil.copy(src, cfg)
                break

    # 데이터 폴더 보장
    for d in (
        "inbox/audio", "inbox/images", "inbox/excel", "inbox/documents", "inbox/notes",
        "vault/raw", "vault/refined", "index",
        "고객DB", "상품DB", "상담기록", "AI작업큐",
    ):
        (ROOT / d).mkdir(parents=True, exist_ok=True)

    # key.txt 안내 파일 (없을 때만)
    keyhint = ROOT / "key.txt.예시"
    if not (ROOT / "key.txt").exists() and not keyhint.exists():
        keyhint.write_text(
            "# 이 파일을 key.txt 로 복사하고 값을 채우세요 (이 폴더에 두면 됩니다)\n"
            "LLM_ENDPOINT=https://lsap.lsware.net\n"
            "LLM_MODEL=qwen3.5-122b-fast\n"
            "LLM_API_KEY=발급받은_API_키\n",
            encoding="utf-8",
        )


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    _setup()
    port = int(os.environ.get("KV_PORT", "8765"))
    from kv.webserver import serve

    serve(port=port, open_browser=True)


if __name__ == "__main__":
    main()
