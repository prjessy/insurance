from __future__ import annotations

from pathlib import Path

from kv.converters.base import BaseConverter, ConvertResult


class HtmlConverter(BaseConverter):
    """저장한 웹페이지(.html) → 텍스트.

    로그인 필요한 사이트는 브라우저에서 로그인 후 '페이지 저장(Ctrl+S)' 한
    .html 을 inbox 에 넣으면 본문 텍스트가 추출된다.
    """

    source_type = "notes"
    extensions = {".html", ".htm"}

    def convert(self, path: Path) -> ConvertResult:
        from kv.webfetch import html_to_text

        raw = path.read_text(encoding="utf-8", errors="replace")
        title, content = html_to_text(raw)
        title = title or path.stem
        body = f"""# {title}

## 원본
- 파일: `{path.name}`
- 유형: HTML(저장된 웹페이지) → 텍스트

## 내용

{content or '(본문 텍스트를 추출하지 못했습니다)'}
"""
        return ConvertResult(title=title, body=body, source_type=self.source_type)
