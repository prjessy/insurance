"""내 자료 기반 질의응답 프롬프트 팩 (로컬 RAG, API 비용 0).

검색 인덱스에서 질문과 관련된 문서를 모아 AI 붙여넣기용 프롬프트로 묶는다.
상용 'second brain Q&A / ask your notes' 기능을 로컬·무비용으로 대체.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from kv.config import profile_folder
from kv.import_refs import vault_root
from kv.search import SearchHit, search


_STOP = {
    "알려줘", "정리", "해줘", "뭐야", "무엇", "어때", "어떻게", "관련", "대해", "대한",
    "그리고", "하지만", "내용", "상황", "어떤", "있어", "없어", "the", "and", "for",
}


def _slug(text: str, n: int = 20) -> str:
    s = re.sub(r"[^\w가-힣 ]", "", text).strip().replace(" ", "-")
    return (s or "질문")[:n]


def _fts_query(question: str) -> str:
    """질문에서 핵심어만 뽑아 OR 질의로. (FTS 기본 AND 회피)"""
    words = re.findall(r"[가-힣]{2,}|[A-Za-z]{2,}|\d{2,}", question)
    terms = [w for w in words if w.lower() not in _STOP]
    terms = list(dict.fromkeys(terms)) or words
    return " OR ".join(f'"{t}"' for t in terms) if terms else question


def ask_pack(question: str, top_k: int = 5, max_chars: int = 1500) -> tuple[Path, list[SearchHit]]:
    hits = search(_fts_query(question), limit=top_k)

    blocks: list[str] = []
    for h in hits:
        try:
            content = Path(h.path).read_text(encoding="utf-8")
        except Exception:
            content = h.snippet
        content = content.strip()
        if len(content) > max_chars:
            content = content[:max_chars].rstrip() + " …(생략)"
        blocks.append(f"### {h.title}\n출처: `{h.path}`\n\n{content}")

    context = "\n\n---\n\n".join(blocks) if blocks else "(검색 결과 없음 — 인덱스를 먼저 만드세요: python -m kv all)"

    prompt = f"""아래 [내 자료]만 근거로 질문에 답해줘.

규칙:
- 질문과 **직접 관련된 내용만** 사용해.
- 자료에 질문과 관련된 내용이 **없으면**, 다른 자료를 끌어다 설명하지 말고
  딱 한 문장으로 **"문서에 관련 내용이 없습니다."** 라고만 답해. (요약·추측 금지)
- 답변에 실제로 근거로 쓴 자료만 끝에 [출처]로 표기해 (관련 자료가 없으면 [출처]도 생략).

[질문]
{question}

[내 자료]
{context}
"""

    # 로컬 LLM 이 켜져 있으면 즉시 답변 생성 (없으면 붙여넣기용 프롬프트만)
    from kv.llm import generate, llm_available

    answer = generate(prompt) if llm_available() else None

    answer_block = ""
    if answer:
        answer_block = f"""## 🤖 자동 답변 (로컬 LLM)

{answer}

---

"""

    body = f"""---
tags: [AI작업큐, painpoint/질의응답]
question: {question}
created: {datetime.now().isoformat()}
answered_by: {"llm-auto" if answer else "manual-paste"}
---

# 내 자료 질의응답

> 검색된 자료 {len(hits)}건을 근거로 답변 (로컬 검색, API 비용 0)

{answer_block}## AI 붙여넣기용 프롬프트 (로컬 LLM 미사용 시)

```
{prompt}
```
"""

    queue = vault_root() / profile_folder("queue")
    queue.mkdir(parents=True, exist_ok=True)
    out = queue / f"{datetime.now().strftime('%Y%m%d_%H%M')}_질문_{_slug(question)}.md"
    out.write_text(body, encoding="utf-8")
    return out, hits, answer
