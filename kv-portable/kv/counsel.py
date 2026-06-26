"""상담 녹취 -> 상담기록 MD (index.html 03단계, 프롬프트 ①)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from kv.config import load_config
from kv.tags import render_markdown
from kv.whisper_stt import format_transcript_markdown, transcribe


def vault_root() -> Path:
    cfg = load_config()
    return Path(cfg["obsidian_vault"]).expanduser().resolve()


def counsel_from_text(text: str, customer: str, channel: str = "대면") -> Path:
    today = date.today().isoformat()
    safe_name = customer.replace("/", "-").strip()
    filename = f"{today}-{safe_name}-상담.md"
    dest = vault_root() / "상담기록" / filename
    dest.parent.mkdir(parents=True, exist_ok=True)

    fm = {
        "type": "상담",
        "고객": f"[[{safe_name}]]",
        "상담일": today,
        "채널": channel,
        "tags": ["상담", "painpoint/녹취정리", "수집/자동"],
        "status": "whisper_done",
        "next_step": "Claude에 프롬프트① 붙여넣기 -> python -m kv pack counsel",
    }

    body = f"""# 핵심 요약
- (AI 정리 대기 — 아래 프롬프트 팩을 Claude에 붙여넣으세요)

# 고객 니즈 / 발언
- 

# 파악된 정보 (→ 고객DB 반영)
- 가족구성: 
- 가입/갱신 변동: 
- 유형태그 변경: 

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
