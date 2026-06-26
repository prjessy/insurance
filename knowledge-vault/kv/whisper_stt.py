"""Whisper 음성 → 텍스트 변환 (openai-whisper / faster-whisper)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from kv.config import load_config


@dataclass
class TranscriptResult:
    text: str
    engine: str
    model: str
    language: str
    duration_sec: float | None = None
    segments: list[dict] | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.text.strip())


def _whisper_cfg() -> dict:
    cfg = load_config()
    w = cfg.get("whisper") or {}
    return {
        "enabled": w.get("enabled", True),
        "engine": w.get("engine", "faster-whisper"),
        "model": w.get("model", "base"),
        "language": w.get("language", "ko"),
        "compute_type": w.get("compute_type", "int8"),
    }


@lru_cache(maxsize=2)
def _load_openai_model(model_name: str):
    import whisper  # type: ignore

    return whisper.load_model(model_name)


@lru_cache(maxsize=2)
def _load_faster_model(model_name: str, compute_type: str):
    from faster_whisper import WhisperModel  # type: ignore

    return WhisperModel(model_name, device="cpu", compute_type=compute_type)


def _transcribe_openai(path: Path, model: str, language: str) -> TranscriptResult:
    import whisper  # type: ignore

    m = _load_openai_model(model)
    result = m.transcribe(str(path), language=language)
    text = (result.get("text") or "").strip()
    segments = [
        {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
        for s in result.get("segments", [])
        if s.get("text", "").strip()
    ]
    return TranscriptResult(
        text=text or "(음성 인식 결과 없음)",
        engine="openai-whisper",
        model=model,
        language=language,
        segments=segments or None,
    )


def _transcribe_faster(path: Path, model: str, language: str, compute_type: str) -> TranscriptResult:
    from faster_whisper import WhisperModel  # type: ignore

    m = _load_faster_model(model, compute_type)
    segments_iter, info = m.transcribe(str(path), language=language, beam_size=5)
    segments: list[dict] = []
    parts: list[str] = []
    for seg in segments_iter:
        t = seg.text.strip()
        if t:
            parts.append(t)
            segments.append({"start": seg.start, "end": seg.end, "text": t})
    return TranscriptResult(
        text=" ".join(parts) or "(음성 인식 결과 없음)",
        engine="faster-whisper",
        model=model,
        language=language,
        duration_sec=getattr(info, "duration", None),
        segments=segments or None,
    )


def transcribe(path: Path) -> TranscriptResult:
    cfg = _whisper_cfg()
    if not cfg["enabled"]:
        return TranscriptResult(
            text="",
            engine="disabled",
            model="",
            language=cfg["language"],
            error="config에서 whisper.enabled=false",
        )

    engine = cfg["engine"]
    model = cfg["model"]
    language = cfg["language"]

    try:
        if engine == "openai-whisper":
            return _transcribe_openai(path, model, language)
        if engine == "faster-whisper":
            return _transcribe_faster(path, model, language, cfg["compute_type"])
        return TranscriptResult(
            text="",
            engine=engine,
            model=model,
            language=language,
            error=f"지원하지 않는 engine: {engine}",
        )
    except ImportError as e:
        pkg = "faster-whisper" if engine == "faster-whisper" else "openai-whisper"
        return TranscriptResult(
            text="",
            engine=engine,
            model=model,
            language=language,
            error=f"{pkg} 미설치 — pip install {pkg}",
        )
    except Exception as e:
        return TranscriptResult(
            text="",
            engine=engine,
            model=model,
            language=language,
            error=str(e),
        )


def format_transcript_markdown(result: TranscriptResult, source_name: str) -> str:
    if result.error:
        return (
            f"(음성 변환 실패: {result.error})\n\n"
            f"녹음 파일: **{source_name}**\n\n"
            "수동 받아쓰기를 아래에 적어 두세요."
        )

    lines = [result.text]
    if result.segments:
        lines.append("\n\n### 타임스탬프\n")
        for s in result.segments:
            start = _fmt_time(s["start"])
            end = _fmt_time(s["end"])
            lines.append(f"- `{start}` - `{end}`: {s['text']}")
    meta = f"\n\n---\n*engine: {result.engine}, model: {result.model}*"
    return "".join(lines) + meta


def _fmt_time(sec: float) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
