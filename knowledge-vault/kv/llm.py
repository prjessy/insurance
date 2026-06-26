"""로컬/외부 LLM 백엔드.

설정(config.yaml 의 llm.enabled)이 켜져 있으면 프롬프트를 자동 실행한다.
실패하면 None 을 반환해 기존 'Claude 붙여넣기' 방식으로 fallback 한다.

지원 provider:
  - ollama  : 로컬/원격 Ollama  (POST {base_url}/api/generate)
  - openai  : OpenAI 호환 API   (POST {base_url}/chat/completions) ← vLLM·LM Studio·사내 게이트웨이·OpenAI 등

보안: API 키는 절대 config/repo 에 저장하지 않는다.
환경변수(기본 KV_LLM_API_KEY)에서만 읽는다.
추가 패키지 불필요 — 표준 라이브러리(urllib)만 사용.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from kv.config import load_config


def _llm_cfg() -> dict:
    return load_config().get("llm", {}) or {}


def _provider() -> str:
    return (_llm_cfg().get("provider") or "ollama").lower()


def _api_key() -> str:
    env_name = _llm_cfg().get("api_key_env", "KV_LLM_API_KEY")
    return os.environ.get(env_name, "").strip()


def llm_enabled() -> bool:
    return bool(_llm_cfg().get("enabled", False))


def _chat_url(base: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def llm_available() -> bool:
    """설정 on + (provider별) 연결 가능 여부."""
    if not llm_enabled():
        return False
    cfg = _llm_cfg()
    if _provider() == "openai":
        # 키 필요 시 키가 있어야 사용 가능 (실 핑은 generate 에서)
        if cfg.get("api_key_env") and not _api_key():
            return False
        return bool(cfg.get("base_url"))
    # ollama: 서버 핑
    base = cfg.get("base_url", "http://localhost:11434").rstrip("/")
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def _post_json(url: str, payload: dict, headers: dict, timeout: int) -> dict | None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def generate(prompt: str, *, system: str | None = None) -> str | None:
    """LLM 으로 프롬프트 실행. 실패 시 None."""
    if not llm_enabled():
        return None
    cfg = _llm_cfg()
    model = cfg.get("model", "qwen2.5")
    timeout = int(cfg.get("timeout", 120))
    system = system or cfg.get("system")

    if _provider() == "openai":
        base = cfg.get("base_url", "").strip()
        if not base:
            return None
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        headers = {}
        key = _api_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        body = _post_json(
            _chat_url(base),
            {"model": model, "messages": messages, "stream": False},
            headers,
            timeout,
        )
        if not body:
            return None
        try:
            return (body["choices"][0]["message"]["content"] or "").strip() or None
        except (KeyError, IndexError, TypeError):
            return None

    # ollama
    base = cfg.get("base_url", "http://localhost:11434").rstrip("/")
    payload: dict = {"model": model, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    body = _post_json(f"{base}/api/generate", payload, {}, timeout)
    if not body:
        return None
    return (body.get("response") or "").strip() or None
