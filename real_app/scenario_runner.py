"""시나리오 실행 엔진 — 웹 데모와 API가 공통으로 사용합니다."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Literal

from real_mcp_server import add_schedule, add_todo, list_schedules, list_todos

LogType = Literal["system", "ai", "tool", "success", "warning", "error"]
ModeId = Literal["1", "2", "3", "4"]

DEFAULT_INTENT = "내일 9시 회의 스케줄 잡고, 할 일에 '자료 준비' 추가해줘"


@dataclass
class LogEntry:
    message: str
    type: LogType = "system"
    delay_ms: int = 800


@dataclass
class ScenarioResult:
    mode: ModeId
    intent: str
    logs: list[LogEntry] = field(default_factory=list)
    result_html: str = ""
    todos: list[dict] = field(default_factory=list)
    schedules: list[dict] = field(default_factory=list)


def reset_databases() -> None:
    import json
    import os

    db_dir = "db_files"
    os.makedirs(db_dir, exist_ok=True)
    with open(os.path.join(db_dir, "todo.json"), "w", encoding="utf-8") as f:
        json.dump([], f)
    with open(os.path.join(db_dir, "schedule.json"), "w", encoding="utf-8") as f:
        json.dump([], f)


def _load_db() -> tuple[list[dict], list[dict]]:
    import json
    import os

    db_dir = "db_files"
    with open(os.path.join(db_dir, "todo.json"), "r", encoding="utf-8") as f:
        todos = json.load(f)
    with open(os.path.join(db_dir, "schedule.json"), "r", encoding="utf-8") as f:
        schedules = json.load(f)
    return todos, schedules


def run_mode1(intent: str = DEFAULT_INTENT) -> ScenarioResult:
    result = ScenarioResult(mode="1", intent=intent)
    result.logs = [
        LogEntry(f"> 👤 사용자: \"{intent}\"", "ai"),
        LogEntry("[단일 AI] 접수 완료. 내장된 스케줄 DB 접속 코드 실행...", "system"),
        LogEntry("⚠️ [경고] DB 접속 코드 포맷 변경으로 일시적 오류 발생 (하드코딩의 단점)", "error"),
        LogEntry("[내부 툴] 스케줄 DB 강제 쓰기 완료.", "tool"),
        LogEntry("[내부 툴] 할 일 DB 파싱 후 쓰기 완료.", "tool"),
        LogEntry("✓ 완료. 그러나 하나가 고장나면 전체 시스템이 멈출 위험 상존.", "error"),
    ]
    result.result_html = "✅ [완료] 단일 AI가 (버벅거리며) 둘 다 처리했습니다."
    return result


def run_mode2(intent: str = DEFAULT_INTENT) -> ScenarioResult:
    result = ScenarioResult(mode="2", intent=intent)
    result.logs = [
        LogEntry(f"> 👤 사용자: \"{intent}\"", "ai"),
        LogEntry("[단일 AI] 접수 완료. 이번엔 외부 도구를 불러오겠습니다.", "system"),
        LogEntry("[MCP 서버 연결] 사용 가능한 도구 목록(Todo, Schedule) 획득 성공!", "success"),
        LogEntry("[단일 AI -> MCP] Schedule 도구 실행 요청 (파라미터: 9시 회의)", "tool"),
        LogEntry("[단일 AI -> MCP] Todo 도구 실행 요청 (파라미터: 자료 준비)", "tool"),
        LogEntry("✓ 완료. 플러그인 연결은 훌륭하나, 한 AI가 두 가지 역할을 다 계산하려니 느립니다.", "warning"),
    ]
    result.result_html = "✅ [완료] AI(1)가 MCP 도구(2개)를 빌려 써서 처리했습니다."
    return result


def run_mode3(intent: str = DEFAULT_INTENT) -> ScenarioResult:
    result = ScenarioResult(mode="3", intent=intent)
    result.logs = [
        LogEntry(f"> 👤 사용자: \"{intent}\"", "ai"),
        LogEntry("[매니저 AI] '할 일'팀과 '일정'팀으로 업무를 안전하게 분할 지시합니다.", "system"),
        LogEntry("[스케줄 에이전트] 9시 회의 스케줄 확인.", "ai"),
        LogEntry(" -> 독자적인 하드코딩된 API로 DB 접속 성공", "tool"),
        LogEntry("[Todo 에이전트] 회의 자료 준비 할 일 확인.", "ai"),
        LogEntry(" -> 옛날 방식의 DB 접속 코드를 자기가 직접 실행 성공", "tool"),
        LogEntry("✓ 업무 분담은 완벽! 하지만 코드가 에이전트마다 분산되어 있어 확장이 힘듭니다.", "warning"),
    ]
    result.result_html = "✅ [완료] 매니저가 지시하고, 서브 에이전트들이 (각자 방식대로) 처리했습니다."
    return result


def run_mode4(intent: str = DEFAULT_INTENT) -> ScenarioResult:
    """실제 MCP 도구를 호출하는 모드 4 — 다중 에이전트 + MCP."""
    reset_databases()
    result = ScenarioResult(mode="4", intent=intent)
    logs: list[LogEntry] = [
        LogEntry(f"> 👤 사용자: \"{intent}\"", "ai"),
        LogEntry("🚀 [최종 아키텍처 가동]", "system"),
        LogEntry("[매니저 AI 허브] 전문 팀들에게 작업 분배 및 권한(MCP 접속 주소) 배포 완료.", "ai"),
        LogEntry("⚡ [다중 에이전트 병렬 처리 시작]", "system"),
    ]

    schedule_msg = add_schedule("09:00", "기획 회의")
    todo_msg = add_todo("회의 자료 준비하기")

    logs.extend([
        LogEntry(" -> [Schedule 에이전트] 공통 MCP 서버의 'Schedule 도구' 호출!", "success", 400),
        LogEntry(f"    {schedule_msg}", "tool", 300),
        LogEntry(" -> [Todo 에이전트] 공통 MCP 서버의 'Todo 도구' 호출!", "success", 400),
        LogEntry(f"    {todo_msg}", "tool", 300),
        LogEntry("★ 퍼펙트! 최고의 보안, 표준화된 연결, 분산된 역할로 순식간에 끝났습니다.", "success"),
    ])

    todos, schedules = _load_db()
    result.logs = logs
    result.todos = todos
    result.schedules = schedules
    result.result_html = (
        "🎉 <strong>[퍼펙트 처리 완료!]</strong><br><br>"
        "다중 AI가 '전문성'을 발휘하고,<br>"
        "MCP로 '안전하고 통일된 도구'를 동시 다발적으로 이용했습니다!<br><br>"
        f"<small>📅 일정: {list_schedules()}<br>📝 할 일: {list_todos()}</small>"
    )
    return result


RUNNERS = {
    "1": run_mode1,
    "2": run_mode2,
    "3": run_mode3,
    "4": run_mode4,
}


def run_scenario(mode: ModeId, intent: str = DEFAULT_INTENT) -> ScenarioResult:
    runner = RUNNERS.get(mode)
    if not runner:
        raise ValueError(f"Unknown mode: {mode}")
    return runner(intent)


def scenario_to_dict(result: ScenarioResult) -> dict:
    return {
        "mode": result.mode,
        "intent": result.intent,
        "logs": [{"message": l.message, "type": l.type, "delay_ms": l.delay_ms} for l in result.logs],
        "result_html": result.result_html,
        "todos": result.todos,
        "schedules": result.schedules,
    }


async def run_all_modes_demo(intent: str = DEFAULT_INTENT) -> list[dict]:
    """4가지 모드를 순서대로 자동 실행 (프레젠테이션 자동화)."""
    results = []
    for mode in ("1", "2", "3", "4"):
        result = run_scenario(mode, intent)
        results.append(scenario_to_dict(result))
        await asyncio.sleep(0.5)
    return results


if __name__ == "__main__":
    for mode in ("1", "2", "3", "4"):
        print(f"\n=== Mode {mode} ===")
        r = run_scenario(mode)
        for log in r.logs:
            print(f"[{log.type}] {log.message}")
        print(r.result_html)
