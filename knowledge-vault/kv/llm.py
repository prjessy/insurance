"""로컬 LLM 백엔드 (Ollama).

설정(config.yaml 의 llm.enabled)이 켜져 있고 Ollama 가 떠 있으면
프롬프트를 로컬에서 자동 실행한다. 실패하면 None 을 반환해
기존 'Claude 붙여넣기' 방식으로 자연스럽게 fallback 한다.

추가 패키지 불필요 — 표준 라이브러리(urllib)만 사용.
모델 예: qwen2.5, exaone3.5, gemma2 등 한국어 가능한 모델.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from kv.config import load_config


def _llm_cfg() -> dict:
    return load_config().get("llm", {}) or {}


def llm_enabled() -> bool:
    return bool(_llm_cfg().get("enabled", False))


def llm_available() -> bool:
    """설정 on + Ollama 서버 응답 확인 (빠른 핑)."""
    if not llm_enabled():
        return False
    cfg = _llm_cfg()
    base = cfg.get("base_url", "http://localhost:11434").rstrip("/")
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def generate(prompt: str, *, system: str | None = None) -> str | None:
    """로컬 LLM 으로 프롬프트 실행. 실패 시 None."""
    if not llm_enabled():
        return None
    cfg = _llm_cfg()
    base = cfg.get("base_url", "http://localhost:11434").rstrip("/")
    model = cfg.get("model", "qwen2.5")
    timeout = int(cfg.get("timeout", 120))

    payload: dict = {"model": model, "prompt": prompt, "stream": False}
    if system or cfg.get("system"):
        payload["system"] = system or cfg.get("system")

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8"))
        return (body.get("response") or "").strip() or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None
