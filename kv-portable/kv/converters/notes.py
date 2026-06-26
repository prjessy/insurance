from __future__ import annotations

from pathlib import Path

from kv.converters.base import BaseConverter, ConvertResult


class NotesConverter(BaseConverter):
    source_type = "notes"
    extensions = {".txt", ".md", ".markdown", ".docx", ".rtf"}

    def convert(self, path: Path) -> ConvertResult:
        content = self._read(path)
        body = f"""# {path.stem}

## 원본
- 파일: `{path.name}`
- 유형: 노트/문서

## 내용

{content}
"""
        return ConvertResult(
            title=path.stem,
            body=body,
            source_type=self.source_type,
        )

    def _read(self, path: Path) -> str:
        ext = path.suffix.lower()
        if ext in {".txt", ".md", ".markdown"}:
            return path.read_text(encoding="utf-8", errors="replace").strip()
        if ext == ".docx":
            try:
                from docx import Document

                doc = Document(path)
                return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
            except Exception as e:
                return f"(docx 읽기 오류: {e})"
        return path.read_text(encoding="utf-8", errors="replace").strip()
