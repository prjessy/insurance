"""URL → 텍스트 → inbox MD (웹사이트 자료 수집).

URL 하나 주면 페이지를 받아 텍스트만 추출해 inbox/notes 에 MD 로 저장한다.
이후 collect/refine/index 로 검색·AI질문에 바로 쓰인다.
표준 라이브러리만 사용(urllib). HTML→텍스트는 가벼운 정규식 변환.
"""

from __future__ import annotations

import html as _html
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from kv.config import INBOX


def _slug(text: str, n: int = 40) -> str:
    s = re.sub(r"[^\w가-힣 -]", "", text).strip().replace(" ", "-")
    return (s or "web")[:n]


def html_to_text(html: str) -> tuple[str, str]:
    """(제목, 본문텍스트) 반환."""
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    title = _html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""
    # 스크립트/스타일 제거
    body = re.sub(r"(?is)<(script|style|noscript|template|svg).*?</\1>", " ", html)
    body = re.sub(r"(?is)<br\s*/?>", "\n", body)
    body = re.sub(r"(?is)</(p|div|li|h[1-6]|tr|section|article)>", "\n", body)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    body = _html.unescape(body)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n+", "\n\n", body).strip()
    return title, body


def fetch_to_inbox(url: str, timeout: int = 20) -> dict:
    """URL 을 받아 inbox/notes 에 MD 저장. {title, file, chars} 반환."""
    if not re.match(r"^https?://", url, re.I):
        raise ValueError("http(s):// URL 만 지원합니다.")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (KnowledgeVault)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        raw = r.read()
    try:
        text = raw.decode(charset, errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")

    title, content = html_to_text(text)
    domain = urlparse(url).netloc
    title = title or domain
    if not content.strip():
        content = "(본문 텍스트를 추출하지 못했습니다)"

    dest = INBOX / "notes" / f"웹_{_slug(title)}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    md = f"""# {title}

## 원본
- URL: {url}
- 수집: {datetime.now().isoformat(timespec='seconds')}

## 내용

{content}
"""
    dest.write_text(md, encoding="utf-8")
    return {"title": title, "file": str(dest), "chars": len(content)}
