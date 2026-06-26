from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from kv.config import VAULT_RAW, VAULT_REFINED, load_config
from kv.tags import build_tags, parse_markdown, render_markdown, slugify


def _extract_keywords(text: str, top_n: int = 12) -> list[str]:
    """간단한 키워드 추출 (AI 없이도 동작)."""
    words = re.findall(r"[가-힣]{2,}|[A-Za-z]{3,}", text)
    stop = {
        "그리고", "하지만", "원본", "유형", "내용", "파일", "시트", "변환",
        "the", "and", "for", "with", "this", "that",
    }
    freq = Counter(w for w in words if w.lower() not in stop)
    return [w for w, _ in freq.most_common(top_n)]


def _summarize(body: str, max_chars: int = 200) -> str:
    lines = []
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if "|" in ln and ln.count("|") >= 2:
            continue
        if ln.startswith("- 파일:") or ln.startswith("- 유형:"):
            continue
        lines.append(ln)
    text = " ".join(lines)
    text = re.sub(r"[`|]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _structure_for_ai(title: str, body: str, keywords: list[str]) -> str:
    summary = _summarize(body)
    kw_line = ", ".join(keywords) if keywords else "(없음)"
    return f"""# {title}

> **AI 요약**: {summary}

## 메타
- **키워드**: {kw_line}
- **정제 목적**: 검색·질의응답에 최적화된 구조

## 핵심 내용

{body}

## 검색 힌트
- 관련 태그로 Obsidian 그래프 연결
- 키워드: {kw_line}
"""


def refine_all(force: bool = False) -> list[Path]:
    """vault/raw → vault/refined (AI 친화 구조 + 추가 태그)."""
    cfg = load_config()
    refined_tag = cfg.get("refined_tag", "상태/정제완료")
    created: list[Path] = []

    for raw_path in sorted(VAULT_RAW.glob("*.md")):
        out_path = VAULT_REFINED / raw_path.name
        if out_path.exists() and not force:
            continue

        text = raw_path.read_text(encoding="utf-8")
        fm, body = parse_markdown(text)
        title = fm.get("title", raw_path.stem)
        keywords = _extract_keywords(body)
        refined_body = _structure_for_ai(title, body, keywords)

        tags = list(fm.get("tags", []))
        if refined_tag not in tags:
            tags.append(refined_tag)

        fm.update({
            "status": "refined",
            "keywords": keywords,
            "summary": _summarize(body),
            "refined_from": raw_path.name,
        })
        fm["tags"] = tags

        out_path.write_text(render_markdown(fm, refined_body), encoding="utf-8")
        created.append(out_path)

    return created
