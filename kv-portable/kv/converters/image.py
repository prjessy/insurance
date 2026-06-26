from __future__ import annotations

from pathlib import Path

from kv.converters.base import BaseConverter, ConvertResult


class ImageConverter(BaseConverter):
    source_type = "image"
    extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}

    def convert(self, path: Path) -> ConvertResult:
        text = self._ocr(path)
        body = f"""# {path.stem}

## 원본
- 파일: `{path.name}`
- 유형: 사진/이미지 → OCR 텍스트

## 추출 텍스트

{text}
"""
        return ConvertResult(
            title=path.stem,
            body=body,
            source_type=self.source_type,
        )

    def _ocr(self, path: Path) -> str:
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(path)
            text = pytesseract.image_to_string(img, lang="kor+eng")
            text = text.strip()
            if text:
                return text
            return "(이미지에서 텍스트를 찾지 못했습니다)"
        except ImportError:
            return (
                "(OCR 불가 — `pip install pytesseract Pillow` 및 "
                "[Tesseract](https://github.com/tesseract-ocr/tesseract) 설치 필요)"
            )
        except Exception as e:
            return f"(OCR 오류: {e})"
