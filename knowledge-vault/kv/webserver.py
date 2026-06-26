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

from kv.config import ROOT, available_profiles, load_profile

WEB_DIR = (ROOT.parent / "kv-web").resolve()


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
        if path == "/api/profile":
            prof = load_profile()
            return self._json(200, {
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
