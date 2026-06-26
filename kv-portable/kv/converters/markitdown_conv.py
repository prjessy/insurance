"""Microsoft MarkItDown 백엔드 변환기.

설치돼 있으면(`pip install markitdown`) PDF·Office·HTML 등 문서를
MarkItDown 으로 변환한다. 실패하거나 미설치면 자체 변환기로 폴백한다.
오디오(Whisper)·이미지(OCR)는 기존 변환기를 그대로 쓰도록 제외한다.
"""

from __future__ import annotations

from pathlib import Path

from kv.converters.base import BaseConverter, ConvertResult

# MarkItDown 에 맡길 확장자 (audio/image 제외)
MARKITDOWN_EXTENSIONS = {
    ".pdf", ".pptx", ".ppt",
    ".xlsx", ".xlsm", ".xls", ".csv", ".tsv",
    ".docx", ".doc", ".rtf",
    ".html", ".htm", ".xml", ".json", ".epub",
}

# MarkItDown 결과에 붙일 source_type (태그 규칙 재사용)
_SUFFIX_TYPE = {
    ".pdf": "pdf",
    ".pptx": "pptx", ".ppt": "pptx",
    ".xlsx": "excel", ".xlsm": "excel", ".xls": "excel", ".csv": "excel", ".tsv": "excel",
}


def markitdown_available() -> bool:
    try:
        import markitdown  # noqa: F401
        return True
    except Exception:
        return False


class MarkItDownConverter(BaseConverter):
    source_type = "document"
    extensions = MARKITDOWN_EXTENSIONS

    def convert(self, path: Path) -> ConvertResult:
        stype = _SUFFIX_TYPE.get(path.suffix.lower(), "notes")
        try:
            from markitdown import MarkItDown

            md = MarkItDown()
            res = md.convert(str(path))
            text = (
                getattr(res, "text_content", None)
                or getattr(res, "markdown", None)
                or ""
            ).strip()
            if not text:
                raise ValueError("빈 변환 결과")
            body = f"""# {path.stem}

## 원본
- 파일: `{path.name}`
- 유형: {path.suffix.lstrip('.').upper()} → Markdown (MarkItDown)

{text}
"""
            return ConvertResult(title=path.stem, body=body, source_type=stype)
        except Exception as e:
            fallback = _native_fallback(path)
            if fallback is not None:
                return fallback
            body = f"# {path.stem}\n\n(MarkItDown 변환 실패: {e})\n"
            return ConvertResult(title=path.stem, body=body, source_type=stype)


def _native_fallback(path: Path) -> ConvertResult | None:
    """MarkItDown 실패 시 자체 변환기로 대체."""
    from kv.converters.excel_conv import ExcelConverter
    from kv.converters.hwp import HwpConverter
    from kv.converters.notes import NotesConverter
    from kv.converters.pdf import PdfConverter
    from kv.converters.pptx_conv import PptxConverter

    for c in (PdfConverter(), PptxConverter(), ExcelConverter(), HwpConverter(), NotesConverter()):
        if c.supports(path):
            return c.convert(path)
    return None
