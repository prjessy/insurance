"""Claude 붙여넣기용 프롬프트 팩 생성 (프롬프트.md 기반)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kv.config import load_config
from kv.import_refs import vault_root


def _queue_dir() -> Path:
    d = vault_root() / "AI작업큐"
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


def _find_customer(name: str) -> Path | None:
    root = vault_root() / "고객DB"
    for p in root.glob("*.md"):
        if p.name.startswith("_"):
            continue
        if name in p.stem or p.stem in name:
            return p
    return None


def _load_products() -> str:
    root = vault_root() / "상품DB"
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
    prompt = _read_prompt_section("①")
    body = f"""---
tags: [AI작업큐, painpoint/녹취정리]
customer: {customer}
created: {datetime.now().isoformat()}
---

# Claude 붙여넣기 — ① 상담 정리

> index.html TO-BE: 녹취 정리 20분 -> 1분

## 프롬프트 (아래 전체 복사 -> Claude)

```
{prompt}
```

## 전사 내용 (프롬프트 안에 이미 포함됨)

{transcript}
"""
    return _write_pack(f"상담정리_{customer or '미지정'}", body)


def pack_propose(customer_name: str) -> Path:
    cust = _find_customer(customer_name)
    if not cust:
        raise FileNotFoundError(f"고객DB에서 '{customer_name}' 을 찾지 못했습니다.")
    prompt = _read_prompt_section("②")
    products = _load_products()
    body = f"""---
tags: [AI작업큐, painpoint/제안서]
customer: {cust.stem}
created: {datetime.now().isoformat()}
---

# Claude 붙여넣기 — ② 맞춤 제안서

> index.html TO-BE: 제안서 30분 -> 2분

```
{prompt}
```

## [고객 정보] (자동 첨부)

{cust.read_text(encoding='utf-8')}

## [상품 목록] (자동 첨부)

{products}
"""
    return _write_pack(f"제안서_{cust.stem}", body)


def pack_message(customer_name: str) -> Path:
    cust = _find_customer(customer_name)
    if not cust:
        raise FileNotFoundError(f"고객DB에서 '{customer_name}' 을 찾지 못했습니다.")
    prompt = _read_prompt_section("③")
    body = f"""---
tags: [AI작업큐, painpoint/안내문자]
customer: {cust.stem}
created: {datetime.now().isoformat()}
---

# Claude 붙여넣기 — ③ 안내 문자

> index.html TO-BE: 문자 작성 10분 -> 30초

```
{prompt}
```

## [고객 정보]

{cust.read_text(encoding='utf-8')}
"""
    return _write_pack(f"문자_{cust.stem}", body)


def pack_excel(excel_path: Path) -> Path:
    from kv.converters.excel_conv import ExcelConverter

    conv = ExcelConverter()
    result = conv.convert(excel_path)
    prompt = _read_prompt_section("④")
    if "④" not in prompt and "자료" not in prompt:
        prompt = _read_prompt_section("①")
    body = f"""---
tags: [AI작업큐, painpoint/엑셀카드]
source: {excel_path.name}
created: {datetime.now().isoformat()}
---

# Claude 붙여넣기 — ④ 엑셀/자료 -> 고객 카드

> index.html: 엑셀 고객명단 -> 카드 형식 변환

```
이 엑셀/자료를 우리 카드 형식으로 정리해줘.
(이름·연락처·가족·갱신일·태그)
고객DB/_고객-템플릿.md 형식을 따라줘.

\"\"\"
{result.body}
\"\"\"
```

## 참고 템플릿

{(vault_root() / '고객DB' / '_고객-템플릿.md').read_text(encoding='utf-8')}
"""
    return _write_pack(f"엑셀변환_{excel_path.stem}", body)
