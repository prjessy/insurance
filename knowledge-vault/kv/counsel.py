"""상담 녹취 -> 상담기록 MD (index.html 03단계, 프롬프트 ①)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from kv.config import (
    load_config,
    profile_folder,
    profile_label,
    profile_record_tags,
    resolve_vault_path,
)
from kv.tags import render_markdown
from kv.whisper_stt import format_transcript_markdown, transcribe


def vault_root() -> Path:
    cfg = load_config()
    return resolve_vault_path(cfg["obsidian_vault"])


def counsel_from_text(text: str, customer: str, channel: str = "대면") -> Path:
    today = date.today().isoformat()
    safe_name = customer.replace("/", "-").strip()
    rec = profile_label("record")            # 상담 / 처리 / 기록
    entity = profile_label("entity")          # 고객 / 요청자 / 대상
    entity_db = profile_folder("entity_db")   # 고객DB / 요청자DB ...
    filename = f"{today}-{safe_name}-{rec}.md"
    dest = vault_root() / profile_folder("records") / filename
    dest.parent.mkdir(parents=True, exist_ok=True)

    fm = {
        "type": rec,
        "entity": f"[[{safe_name}]]",
        profile_label("date"): today,
        profile_label("channel"): channel,
        "tags": profile_record_tags(),
        "status": "whisper_done",
        "next_step": "Claude에 정리 프롬프트 붙여넣기 -> python -m kv pack counsel",
    }

    body = f"""# 핵심 요약
- (AI 정리 대기 — 아래 프롬프트 팩을 Claude에 붙여넣으세요)

# {entity} 니즈 / 발언
-

# 파악된 정보 (→ {entity_db} 반영)
-

# 다음 액션
- [ ]

---

## 원본 전사 (Whisper/수동)

{text.strip()}
"""
    dest.write_text(render_markdown(fm, body), encoding="utf-8")
    return dest


def counsel_from_audio(audio_path: Path, customer: str, channel: str = "대면") -> tuple[Path, str]:
    result = transcribe(audio_path)
    text = format_transcript_markdown(result, audio_path.name)
    path = counsel_from_text(text, customer, channel)
    return path, text


def counsel_from_file(path: Path, customer: str, channel: str = "대면") -> Path:
    if path.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}:
        dest, _ = counsel_from_audio(path, customer, channel)
        return dest
    text = path.read_text(encoding="utf-8")
    return counsel_from_text(text, customer, channel)
