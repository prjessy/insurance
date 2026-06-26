from __future__ import annotations

from pathlib import Path

from kv.converters.audio import AudioConverter
from kv.converters.base import BaseConverter
from kv.converters.excel_conv import ExcelConverter
from kv.converters.hwp import HwpConverter
from kv.converters.image import ImageConverter
from kv.converters.notes import NotesConverter
from kv.converters.pdf import PdfConverter
from kv.converters.pptx_conv import PptxConverter

ALL_CONVERTERS: list[BaseConverter] = [
    AudioConverter(),
    ImageConverter(),
    ExcelConverter(),
    PdfConverter(),
    PptxConverter(),
    HwpConverter(),
    NotesConverter(),
]

INBOX_TYPE_MAP = {
    "audio": AudioConverter(),
    "images": ImageConverter(),
    "excel": ExcelConverter(),
    "notes": NotesConverter(),
    # documents 폴더에는 pdf/pptx/hwp 가 섞일 수 있으므로 supports() 실패 시
    # converter_for 가 ALL_CONVERTERS 로 자동 폴백한다.
    "documents": PdfConverter(),
}


def converter_for(path: Path, inbox_root: Path | None = None) -> BaseConverter | None:
    if inbox_root:
        try:
            rel = path.relative_to(inbox_root)
            top = rel.parts[0] if rel.parts else ""
            if top in INBOX_TYPE_MAP and INBOX_TYPE_MAP[top].supports(path):
                return INBOX_TYPE_MAP[top]
        except ValueError:
            pass
    for c in ALL_CONVERTERS:
        if c.supports(path):
            return c
    return None
