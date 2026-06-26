"""
Knowledge Vault Portable Launcher
- 웹 UI 서빙 (kv-web)
- Whisper 녹음 -> 텍스트 API
- Python 설치 없이 exe로 실행 가능 (PyInstaller 빌드)
"""
from __future__ import annotations

import os
import sys
import tempfile
import webbrowser
from datetime import date
from pathlib import Path

# PyInstaller 번들 경로
if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    BUNDLE_DIR = Path(__file__).resolve().parent
    APP_DIR = BUNDLE_DIR

WEB_DIR = BUNDLE_DIR / "kv-web"
VAULT_DIR = APP_DIR / "vault_data"
PORT = int(os.environ.get("KV_PORT", "8765"))

# knowledge-vault 모듈 경로
KV_PKG = BUNDLE_DIR / "kv"
if KV_PKG.is_dir() and str(BUNDLE_DIR) not in sys.path:
    sys.path.insert(0, str(BUNDLE_DIR))


def ensure_dirs() -> None:
    for sub in ("inbox/audio", "inbox/notes", "inbox/excel", "inbox/images",
                "output/상담기록", "output/KnowledgeVault", "output/AI작업큐"):
        (VAULT_DIR / sub).mkdir(parents=True, exist_ok=True)


def transcribe_audio(file_path: Path) -> dict:
    try:
        from kv.whisper_stt import transcribe, format_transcript_markdown
        result = transcribe(file_path)
        text = format_transcript_markdown(result, file_path.name)
        return {
            "ok": result.ok,
            "text": text,
            "engine": result.engine,
            "model": result.model,
            "error": result.error,
        }
    except ImportError:
        return {"ok": False, "text": "", "error": "faster-whisper 미포함 — 개발 모드에서 pip install faster-whisper"}


def create_app():
    from fastapi import FastAPI, File, Form, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles

    app = FastAPI(title="Knowledge Vault Portable")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "mode": "portable",
            "whisper": True,
            "vault_dir": str(VAULT_DIR),
        }

    @app.post("/api/transcribe")
    async def api_transcribe(file: UploadFile = File(...)):
        suffix = Path(file.filename or "audio.mp3").suffix or ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        try:
            result = transcribe_audio(tmp_path)
            # inbox에 원본 저장
            dest = VAULT_DIR / "inbox" / "audio" / (file.filename or "recording.mp3")
            dest.write_bytes(content)
            return result
        finally:
            tmp_path.unlink(missing_ok=True)

    @app.post("/api/counsel")
    async def api_counsel(
        file: UploadFile = File(None),
        text: str = Form(""),
        customer: str = Form(...),
        channel: str = Form("대면"),
    ):
        transcript = text.strip()
        if file and file.filename:
            suffix = Path(file.filename).suffix or ".mp3"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = Path(tmp.name)
            try:
                tr = transcribe_audio(tmp_path)
                transcript = tr.get("text", "") or transcript
                (VAULT_DIR / "inbox" / "audio" / file.filename).write_bytes(content)
            finally:
                tmp_path.unlink(missing_ok=True)

        today = date.today().isoformat()
        safe = customer.replace("/", "-").strip()
        fname = f"{today}-{safe}-상담.md"
        body = f"""---
type: 상담
고객: "[[{safe}]]"
상담일: {today}
채널: {channel}
tags:
  - 상담
  - painpoint/녹취정리
  - 수집/자동
---

# 핵심 요약
- (Claude 프롬프트 ①로 정리하세요)

# 고객 니즈 / 발언
-

# 파악된 정보 (→ 고객DB 반영)
- 가족구성:
- 가입/갱신 변동:
- 유형태그 변경:

# 다음 액션
- [ ]

---

## 원본 전사

{transcript}
"""
        out = VAULT_DIR / "output" / "상담기록" / fname
        out.write_text(body, encoding="utf-8")
        return {"ok": True, "path": str(out), "transcript": transcript}

    @app.get("/api/vault-path")
    def vault_path():
        return {"path": str(VAULT_DIR)}

    if WEB_DIR.is_dir():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
    return app


def main():
    ensure_dirs()
    try:
        import uvicorn
    except ImportError:
        print("uvicorn 필요: pip install uvicorn fastapi")
        sys.exit(1)

    url = f"http://127.0.0.1:{PORT}"
    print("=" * 50)
    print("  Knowledge Vault Portable")
    print("  Python 설치 불필요 (exe 모드)")
    print("=" * 50)
    print(f"  브라우저: {url}")
    print(f"  데이터:   {VAULT_DIR}")
    print("  종료: 이 창을 닫거나 Ctrl+C")
    print("=" * 50)

    webbrowser.open(url)
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
