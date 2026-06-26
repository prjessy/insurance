"""웹 백엔드 (표준 라이브러리만, 추가 패키지 불필요).

kv-web 정적 파일 + kv 모듈 기반 API 를 함께 서빙한다.
LLM·프로파일·검색·질의응답을 브라우저에서 바로 쓸 수 있게 한다.

  GET  /api/health     상태 + LLM 사용 가능 여부
  GET  /api/profile    활성 프로파일(카테고리/용어/폴더) + 전환 가능 목록
  POST /api/ask        {question, top} → 내 자료 검색 + (LLM)자동 답변
  POST /api/search     {query} → 검색 결과
"""

from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from kv.config import BUNDLE_DIR, ROOT, available_profiles, load_profile


def _web_dir() -> Path:
    """kv-web 정적 폴더 위치 (개발=형제 폴더, exe=번들/exe 옆)."""
    for cand in (BUNDLE_DIR / "kv-web", ROOT / "kv-web", ROOT.parent / "kv-web"):
        if cand.is_dir():
            return cand.resolve()
    return (ROOT.parent / "kv-web").resolve()


WEB_DIR = _web_dir()

_AUDIO = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
_IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}
_EXCEL = {".xlsx", ".xlsm", ".xltx", ".xls", ".csv", ".tsv"}
_DOCS = {".pdf", ".pptx", ".ppt", ".hwp", ".hwpx"}


def _inbox_subdir(ext: str) -> str:
    ext = ext.lower()
    if ext in _AUDIO:
        return "audio"
    if ext in _IMAGE:
        return "images"
    if ext in _EXCEL:
        return "excel"
    if ext in _DOCS:
        return "documents"
    return "notes"


def _parse_date(val) -> "datetime.date | None":
    import datetime as _dt

    if not val:
        return None
    s = str(val)[:10]
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return _dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _dashboard() -> dict:
    """고객DB(프로파일 entity_db) frontmatter 집계 — Obsidian 없이 웹 대시보드."""
    import datetime as _dt

    from kv.config import profile_folder, profile_label
    from kv.import_refs import vault_root
    from kv.tags import parse_markdown

    root = vault_root()
    folder = (root / profile_folder("entity_db")) if root else None
    rows: list[dict] = []
    if folder and folder.exists():
        for md in sorted(folder.glob("*.md")):
            if md.name.startswith("_"):
                continue
            try:
                fm, _ = parse_markdown(md.read_text(encoding="utf-8"))
            except Exception:
                continue
            # 날짜 후보 (…갱신일/일자 등)
            date_val = None
            for k, v in fm.items():
                if any(t in str(k) for t in ("갱신", "일자", "날짜", "date")):
                    date_val = date_val or _parse_date(v)
            tags = fm.get("유형태그") or fm.get("tags") or fm.get("태그") or ""
            if isinstance(tags, list):
                tags = ", ".join(str(t) for t in tags)
            rows.append({
                "name": md.stem,
                "next_date": date_val.isoformat() if date_val else "",
                "tags": str(tags),
                "contact": str(fm.get("연락처") or fm.get("contact") or ""),
                "_days": (date_val - _dt.date.today()).days if date_val else None,
            })

    renewal = sorted(
        [r for r in rows if r["_days"] is not None and 0 <= r["_days"] <= 60],
        key=lambda r: r["_days"],
    )
    by_tag: dict[str, int] = {}
    for r in rows:
        for t in [x.strip() for x in r["tags"].replace("#", "").split(",") if x.strip()]:
            by_tag[t] = by_tag.get(t, 0) + 1

    return {
        "entity_label": profile_label("entity"),
        "total": len(rows),
        "renewal_soon": renewal,
        "by_tag": by_tag,
        "all": rows,
    }


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, obj: dict) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    # ---- GET ----
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            from kv.llm import _model, llm_available, llm_enabled

            return self._json(200, {
                "ok": True,
                "llm_enabled": llm_enabled(),
                "llm_available": llm_available(),
                "model": _model(),
            })
        if path == "/api/dashboard":
            return self._json(200, _dashboard())
        if path == "/api/profile":
            from kv.config import load_config

            prof = load_profile()
            return self._json(200, {
                "active": load_config().get("profile") or "finance",
                "name": prof.get("name"),
                "category": prof.get("category"),
                "labels": prof.get("labels", {}),
                "folders": prof.get("folders", {}),
                "available": available_profiles(),
            })
        return self._serve_static(path)

    # ---- POST ----
    def do_POST(self) -> None:
        path = urlparse(self.path).path
        data = self._read_body()
        if path == "/api/ask":
            q = (data.get("question") or "").strip()
            if not q:
                return self._json(400, {"error": "question 이 비어 있습니다."})
            from kv.ask import ask_pack

            out, hits, answer = ask_pack(q, top_k=int(data.get("top", 5)))
            return self._json(200, {
                "answer": answer,
                "hits": [{"title": h.title, "path": h.path, "snippet": h.snippet} for h in hits],
                "file": str(out),
            })
        if path == "/api/profile":
            import re

            from kv.config import CONFIG_PATH, available_profiles

            name = (data.get("profile") or "").strip()
            if name not in available_profiles():
                return self._json(400, {"error": f"알 수 없는 프로파일: {name}"})
            try:
                txt = CONFIG_PATH.read_text(encoding="utf-8") if CONFIG_PATH.exists() else ""
                if re.search(r"(?m)^profile:\s*.*$", txt):
                    txt = re.sub(r"(?m)^profile:\s*.*$", f"profile: {name}", txt, count=1)
                else:
                    txt = f"profile: {name}\n" + txt
                CONFIG_PATH.write_text(txt, encoding="utf-8")
            except Exception as e:
                return self._json(500, {"error": f"저장 실패: {e}"})
            return self._json(200, {"ok": True, "profile": name})
        if path == "/api/collect":
            import base64

            from kv.config import INBOX

            fn = (data.get("filename") or "").strip().replace("/", "_").replace("\\", "_")
            b64 = data.get("data_base64") or ""
            if not fn or not b64:
                return self._json(400, {"error": "filename / data_base64 가 필요합니다."})
            try:
                raw = base64.b64decode(b64.split(",")[-1])
            except Exception:
                return self._json(400, {"error": "파일 디코딩 실패"})
            sub = _inbox_subdir(Path(fn).suffix)
            dest = INBOX / sub / fn
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)

            from kv.ingest import collect_inbox
            from kv.refine import refine_all
            from kv.search import rebuild_index

            collect_inbox(force=False)
            refine_all(force=False)
            n = rebuild_index()
            return self._json(200, {"ok": True, "file": fn, "type": sub, "indexed": n})
        if path == "/api/fetch-url":
            url = (data.get("url") or "").strip()
            if not url:
                return self._json(400, {"error": "url 이 필요합니다."})
            from kv.ingest import collect_inbox
            from kv.refine import refine_all
            from kv.search import rebuild_index
            from kv.webfetch import fetch_to_inbox

            try:
                info = fetch_to_inbox(url)
            except Exception as e:
                return self._json(400, {"error": f"가져오기 실패: {e}"})
            collect_inbox(force=False)
            refine_all(force=False)
            n = rebuild_index()
            return self._json(200, {"ok": True, "title": info["title"],
                                    "chars": info["chars"], "indexed": n})
        if path == "/api/pack":
            mode = (data.get("mode") or "").strip()
            target = (data.get("target") or data.get("customer") or "").strip()
            transcript = data.get("transcript") or ""
            from kv.prompt_pack import pack_and_answer

            try:
                r = pack_and_answer(mode, target, transcript)
            except FileNotFoundError as e:
                return self._json(404, {"error": str(e)})
            except Exception as e:
                return self._json(400, {"error": str(e)})
            return self._json(200, {"ok": True, **r})
        if path == "/api/search":
            q = (data.get("query") or "").strip()
            if not q:
                return self._json(400, {"error": "query 가 비어 있습니다."})
            from kv.ask import _fts_query
            from kv.search import search

            hits = search(_fts_query(q), limit=int(data.get("limit", 10)))
            return self._json(200, {
                "hits": [{"title": h.title, "path": h.path, "snippet": h.snippet,
                          "tags": h.tags} for h in hits],
            })
        return self._json(404, {"error": "not found"})

    # ---- 정적 파일 ----
    def _serve_static(self, path: str) -> None:
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (WEB_DIR / rel).resolve()
        if not str(target).startswith(str(WEB_DIR)) or not target.is_file():
            return self._json(404, {"error": "not found"})
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:  # 조용히
        pass


def serve(port: int = 8765, open_browser: bool = True) -> None:
    prof = load_profile()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print("=" * 52)
    print("  Knowledge Vault Web  (LLM·프로파일 연동)")
    print(f"  카테고리: {prof.get('category')} / {prof.get('name')}")
    print(f"  브라우저: {url}")
    print("  종료: Ctrl+C")
    print("=" * 52)
    if open_browser:
        try:
            import webbrowser

            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
