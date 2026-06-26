from __future__ import annotations

import re
import zipfile
from pathlib import Path

from kv.converters.base import BaseConverter, ConvertResult


class HwpConverter(BaseConverter):
    """한글(HWP/HWPX) 문서 → 텍스트 (best-effort)."""

    source_type = "hwp"
    extensions = {".hwp", ".hwpx"}

    def convert(self, path: Path) -> ConvertResult:
        if path.suffix.lower() == ".hwpx":
            text = self._extract_hwpx(path)
        else:
            text = self._extract_hwp(path)
        body = f"""# {path.stem}

## 원본
- 파일: `{path.name}`
- 유형: 한글(HWP) → 텍스트 추출

## 내용

{text}
"""
        return ConvertResult(title=path.stem, body=body, source_type=self.source_type)

    def _extract_hwpx(self, path: Path) -> str:
        try:
            parts: list[str] = []
            with zipfile.ZipFile(path) as z:
                names = sorted(n for n in z.namelist() if re.search(r"section\d+\.xml$", n))
                for n in names:
                    xml = z.read(n).decode("utf-8", errors="replace")
                    # <hp:t> ... </hp:t> 안의 텍스트만 추출
                    chunks = re.findall(r"<hp:t>(.*?)</hp:t>", xml, flags=re.DOTALL)
                    if not chunks:
                        chunks = re.findall(r"<[^>]*:t>(.*?)</[^>]*:t>", xml, flags=re.DOTALL)
                    text = "\n".join(re.sub(r"<[^>]+>", "", c) for c in chunks)
                    if text.strip():
                        parts.append(text)
            text = "\n".join(parts).strip()
            return text or "(HWPX에서 텍스트를 찾지 못했습니다)"
        except Exception as e:
            return f"(HWPX 변환 오류: {e})"

    def _extract_hwp(self, path: Path) -> str:
        try:
            import olefile
        except ImportError:
            return "(HWP 불가 — `pip install olefile` 필요)"
        try:
            ole = olefile.OleFileIO(str(path))
            # PrvText: UTF-16LE 미리보기 텍스트 (가장 간단·안정적)
            if ole.exists("PrvText"):
                data = ole.openstream("PrvText").read()
                ole.close()
                text = data.decode("utf-16-le", errors="replace").strip()
                if text:
                    return text
            ole.close()
            return (
                "(HWP 본문 추출 제한 — 미리보기 텍스트 없음. "
                "한글에서 '다른 이름으로 저장 → 텍스트/HWPX' 후 재시도 권장)"
            )
        except Exception as e:
            return f"(HWP 변환 오류: {e})"
