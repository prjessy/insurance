from __future__ import annotations

from pathlib import Path

from kv.converters.base import BaseConverter, ConvertResult
from kv.whisper_stt import format_transcript_markdown, transcribe


class AudioConverter(BaseConverter):
    source_type = "audio"
    extensions = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}

    def convert(self, path: Path) -> ConvertResult:
        result = transcribe(path)
        text = format_transcript_markdown(result, path.name)
        body = f"""# {path.stem}

## 원본
- 파일: `{path.name}`
- 유형: 녹음 → Whisper 텍스트

## 변환 텍스트

{text}
"""
        extra = {
            "whisper_engine": result.engine,
            "whisper_model": result.model,
            "whisper_language": result.language,
        }
        if result.duration_sec is not None:
            extra["audio_duration_sec"] = round(result.duration_sec, 1)
        if result.error:
            extra["whisper_error"] = result.error

        return ConvertResult(
            title=path.stem,
            body=body,
            source_type=self.source_type,
            extra_meta=extra,
        )
