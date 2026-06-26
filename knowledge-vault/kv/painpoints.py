"""
index.html pain point -> 해결 명령 매핑.

AS-IS (80분/고객):
  - 녹음 다시 듣고 정리 20분
  - 엑셀에서 고객 찾기 5분
  - 제안서 직접 작성 30분
  - 안내 문자 고민 10분
  - 갱신 고객 엑셀 확인 15분

TO-BE (6분/고객): kv 명령으로 연결
"""

from __future__ import annotations

PAIN_POINTS = [
    {
        "id": "scatter",
        "chip": "흩어진 정보",
        "sources": ["상담 수첩", "엑셀", "카톡", "통화 메모", "가입 서류", "머릿속"],
        "asis": "여기저기 흩어져 찾기 어려움",
        "tobe": "inbox에 넣으면 태그 MD로 한곳에 모음",
        "command": "python -m kv all",
        "inbox": "inbox/notes, excel, images, audio",
    },
    {
        "id": "transcript",
        "chip": "녹취 정리",
        "asis": "20분",
        "tobe": "1분",
        "command": "python -m kv counsel --audio inbox/audio/파일.mp3 --customer 고객명",
        "alt": "python -m kv counsel --text inbox/notes/전사.txt --customer 고객명",
    },
    {
        "id": "find_customer",
        "chip": "고객 찾기",
        "asis": "엑셀에서 5분",
        "tobe": "즉시 검색",
        "command": 'python -m kv search "고객이름"',
    },
    {
        "id": "proposal",
        "chip": "제안서 작성",
        "asis": "30분",
        "tobe": "2분 (AI 초안)",
        "command": "python -m kv pack propose 정수남",
    },
    {
        "id": "message",
        "chip": "안내 문자",
        "asis": "10분",
        "tobe": "30초 (AI 초안)",
        "command": "python -m kv pack message 정수남",
    },
    {
        "id": "renewal",
        "chip": "갱신 고객 찾기",
        "asis": "엑셀 15분",
        "tobe": "대시보드 자동 (0분)",
        "command": "Obsidian에서 대시보드.md 열기 (Dataview)",
    },
    {
        "id": "excel_card",
        "chip": "엑셀 -> 고객 카드",
        "asis": "수동 입력",
        "tobe": "AI 프롬프트 팩 자동 생성",
        "command": "python -m kv pack excel inbox/excel/명단.xlsx",
    },
]


def print_painpoints() -> None:
    print("=== index.html Pain Point -> 해결 방법 ===\n")
    print("AS-IS: 고객 1명당 약 80분  ->  TO-BE: 약 6분\n")
    for i, p in enumerate(PAIN_POINTS, 1):
        print(f"[{i}] {p['chip']}")
        if p.get("sources"):
            print(f"    문제: {', '.join(p['sources'])}")
        if p.get("asis") and p.get("tobe"):
            print(f"    {p['asis']} -> {p['tobe']}")
        print(f"    >> {p['command']}")
        if p.get("inbox"):
            print(f"    넣는 곳: {p['inbox']}")
        if p.get("alt"):
            print(f"    또는: {p['alt']}")
        print()
