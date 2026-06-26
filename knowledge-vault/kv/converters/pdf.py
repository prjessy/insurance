from __future__ import annotations

from pathlib import Path

from kv.converters.base import BaseConverter, ConvertResult


class PdfConverter(BaseConverter):
    source_type = "pdf"
    extensions = {".pdf"}

    def convert(self, path: Path) -> ConvertResult:
        text = self._extract(path)
        body = f"""# {path.stem}

## 원본
- 파일: `{path.name}`
- 유형: PDF → 텍스트 추출

## 내용

{text}
"""
        return ConvertResult(title=path.stem, body=body, source_type=self.source_type)

    def _extract(self, path: Path) -> str:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            parts: list[str] = []
            for i, page in enumerate(reader.pages, 1):
                t = (page.extract_text() or "").strip()
                if t:
                    parts.append(f"### p.{i}\n\n{t}")
            text = "\n\n".join(parts).strip()
            if text:
                return text
            return (
                "(텍스트를 찾지 못했습니다 — 스캔 PDF일 수 있습니다. "
                "이미지로 변환 후 OCR(inbox/images)을 사용하세요)"
            )
        except ImportError:
            return "(PDF 불가 — `pip install pypdf` 필요)"
        except Exception as e:
            return f"(PDF 변환 오류: {e})"
