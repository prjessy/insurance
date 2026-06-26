"""AI 붙여넣기용 프롬프트 팩 생성.

도메인 용어/폴더는 활성 프로파일(config.py load_profile)에서 가져온다.
프로파일에 prompts 가 정의돼 있으면 그것을, 없으면 vault 의 프롬프트.md 섹션을 쓴다.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kv.config import profile_folder, profile_label, profile_prompt
from kv.import_refs import vault_root


def _queue_dir() -> Path:
    d = vault_root() / profile_folder("queue")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _read_prompt_section(section: str) -> str:
    root = vault_root()
    prompt_md = root / "프롬프트.md"
    if not prompt_md.exists():
        return f"(프롬프트.md 없음: {section})"
    text = prompt_md.read_text(encoding="utf-8")
    markers = {"①": "## ①", "②": "## ②", "③": "## ③", "④": "## ④"}
    start = markers.get(section, "")
    if not start:
        return text
    idx = text.find(start)
    if idx < 0:
        return text
    nxt = text.find("\n## ", idx + 3)
    block = text[idx:nxt] if nxt > 0 else text[idx:]
    # 코드블록 안의 프롬프트만 추출
    if "```" in block:
        parts = block.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 1 and part.strip():
                return part.strip()
    return block


def _prompt(key: str, section: str) -> str:
    """프로파일 프롬프트 우선, 없으면 프롬프트.md 섹션 fallback."""
    p = profile_prompt(key)
    return p if p else _read_prompt_section(section)


def _find_entity(name: str) -> Path | None:
    root = vault_root() / profile_folder("entity_db")
    if not root.exists():
        return None
    for p in root.glob("*.md"):
        if p.name.startswith("_"):
            continue
        if name in p.stem or p.stem in name:
            return p
    return None


def _entity_template() -> str:
    root = vault_root() / profile_folder("entity_db")
    if root.exists():
        for p in sorted(root.glob("_*.md")):
            return p.read_text(encoding="utf-8")
    return "(템플릿 없음)"


def _load_catalog() -> str:
    root = vault_root() / profile_folder("catalog_db")
    if not root.exists():
        return "(목록 없음)"
    parts = []
    for p in sorted(root.glob("*.md")):
        if p.name.startswith("_"):
            continue
        parts.append(f"### {p.stem}\n\n{p.read_text(encoding='utf-8')}\n")
    return "\n".join(parts)


def _write_pack(name: str, content: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    path = _queue_dir() / f"{ts}_{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


def pack_counsel(transcript: str, customer: str = "") -> Path:
    rec = profile_label("record")
    prompt = _prompt("summarize", "①")
    body = f"""---
tags: [AI작업큐, painpoint/녹취정리]
entity: {customer}
created: {datetime.now().isoformat()}
---

# AI 붙여넣기 — {rec} 정리

> 녹취 정리 20분 -> 1분

## 프롬프트 (아래 전체 복사 -> AI)

```
{prompt}
```

## 전사 내용 (프롬프트 안에 이미 포함됨)

{transcript}
"""
    return _write_pack(f"{rec}정리_{customer or '미지정'}", body)


def pack_propose(entity_name: str) -> Path:
    ent = _find_entity(entity_name)
    entity_label = profile_label("entity")
    if not ent:
        raise FileNotFoundError(
            f"{profile_folder('entity_db')}에서 '{entity_name}' 을 찾지 못했습니다."
        )
    proposal = profile_label("proposal")
    prompt = _prompt("propose", "②")
    catalog = _load_catalog()
    body = f"""---
tags: [AI작업큐, painpoint/제안서]
entity: {ent.stem}
created: {datetime.now().isoformat()}
---

# AI 붙여넣기 — {proposal}

> 제안서 30분 -> 2분

```
{prompt}
```

## [{entity_label} 정보] (자동 첨부)

{ent.read_text(encoding='utf-8')}

## [{profile_label('catalog')} 목록] (자동 첨부)

{catalog}
"""
    return _write_pack(f"{proposal}_{ent.stem}", body)


def pack_message(entity_name: str) -> Path:
    ent = _find_entity(entity_name)
    entity_label = profile_label("entity")
    if not ent:
        raise FileNotFoundError(
            f"{profile_folder('entity_db')}에서 '{entity_name}' 을 찾지 못했습니다."
        )
    message = profile_label("message")
    prompt = _prompt("message", "③")
    body = f"""---
tags: [AI작업큐, painpoint/안내문자]
entity: {ent.stem}
created: {datetime.now().isoformat()}
---

# AI 붙여넣기 — {message}

> 문자 작성 10분 -> 30초

```
{prompt}
```

## [{entity_label} 정보]

{ent.read_text(encoding='utf-8')}
"""
    return _write_pack(f"{message}_{ent.stem}", body)


def _compose(mode: str, target: str = "", transcript: str = "") -> tuple[str, str, str]:
    """(저장명, 제목, LLM에 보낼 전체 프롬프트) 반환."""
    if mode == "counsel":
        rec = profile_label("record")
        full = _prompt("summarize", "①") + f"\n\n[전사 내용]\n{transcript}"
        return f"{rec}정리_{target or '미지정'}", f"{rec} 정리", full
    if mode in ("propose", "message"):
        ent = _find_entity(target)
        if not ent:
            raise FileNotFoundError(
                f"{profile_folder('entity_db')}에서 '{target}' 을 찾지 못했습니다."
            )
        elabel = profile_label("entity")
        info = ent.read_text(encoding="utf-8")
        if mode == "propose":
            full = (_prompt("propose", "②")
                    + f"\n\n[{elabel} 정보]\n{info}\n\n[{profile_label('catalog')} 목록]\n{_load_catalog()}")
            return f"{profile_label('proposal')}_{ent.stem}", profile_label("proposal"), full
        full = _prompt("message", "③") + f"\n\n[{elabel} 정보]\n{info}"
        return f"{profile_label('message')}_{ent.stem}", profile_label("message"), full
    raise ValueError(f"알 수 없는 모드: {mode}")


def pack_and_answer(mode: str, target: str = "", transcript: str = "") -> dict:
    """프롬프트 구성 → LLM 있으면 자동 생성, 없으면 프롬프트만. 큐에 저장."""
    from kv.llm import generate, llm_available

    name, title, prompt = _compose(mode, target, transcript)
    answer = generate(prompt) if llm_available() else None
    block = f"## 🤖 자동 생성 (LLM)\n\n{answer}\n\n---\n\n" if answer else ""
    body = f"""---
tags: [AI작업큐, {mode}]
created: {datetime.now().isoformat()}
answered_by: {"llm-auto" if answer else "manual-paste"}
---

# {title}

{block}## 프롬프트 (LLM 없을 때 외부 AI에 복사)

```
{prompt}
```
"""
    out = _write_pack(name, body)
    return {"title": title, "prompt": prompt, "answer": answer, "file": str(out)}


def pack_excel(excel_path: Path) -> Path:
    from kv.converters.excel_conv import ExcelConverter

    conv = ExcelConverter()
    result = conv.convert(excel_path)
    entity_label = profile_label("entity")
    body = f"""---
tags: [AI작업큐, painpoint/엑셀카드]
source: {excel_path.name}
created: {datetime.now().isoformat()}
---

# AI 붙여넣기 — 엑셀/자료 -> {entity_label} 카드

> 엑셀 명단 -> 카드 형식 변환

```
이 엑셀/자료를 우리 {entity_label} 카드 형식으로 정리해줘.
아래 참고 템플릿의 형식(YAML frontmatter)을 따라줘.
추측하지 말고 자료에 있는 정보만 사용해.

\"\"\"
{result.body}
\"\"\"
```

## 참고 템플릿

{_entity_template()}
"""
    return _write_pack(f"엑셀변환_{excel_path.stem}", body)
