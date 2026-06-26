# real_mcp_server.py
# 이 파이썬 파일은 오직 "DB를 읽고 쓰는 작업"만 전문적으로 수행하는 '도구(MCP) 서버'입니다.
# 어떤 뇌(AI)가 접속하든 상관없이 똑같은 표준화된 방법으로 도구를 빌려줍니다.
import json
import os
from mcp.server.fastmcp import FastMCP

# 데이터베이스(텍스트 파일) 경로
DB_DIR = "db_files"
TODO_DB = f"{DB_DIR}/todo.json"
SCHEDULE_DB = f"{DB_DIR}/schedule.json"

# 폴더 및 빈 파일 생성 (처음 실행 시)
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
if not os.path.exists(TODO_DB):
    with open(TODO_DB, "w", encoding="utf-8") as f: json.dump([], f)
if not os.path.exists(SCHEDULE_DB):
    with open(SCHEDULE_DB, "w", encoding="utf-8") as f: json.dump([], f)

# 새로운 MCP 서버 인스턴스 생성
mcp = FastMCP("My_Smart_Life_Tools")

# 1. 할 일 툴 (Todo Tool) - 추가하기
@mcp.tool()
def add_todo(task: str) -> str:
    """새로운 할 일을 추가합니다."""
    with open(TODO_DB, "r", encoding="utf-8") as f: data = json.load(f)
    new_id = len(data) + 1
    data.append({"id": new_id, "task": task, "done": False})
    with open(TODO_DB, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    return f"완료: [할 일 - {task}] 항목이 저장되었습니다!"

# 2. 할 일 툴 - 목록 보기
@mcp.tool()
def list_todos() -> str:
    """현재 저장된 모든 할 일을 보여줍니다."""
    with open(TODO_DB, "r", encoding="utf-8") as f: data = json.load(f)
    if not data: return "등록된 할 일이 없습니다."
    return "\n".join([f"- {d['id']}. {d['task']} (완료여부: {d['done']})" for d in data])

# 3. 스케줄 툴 - 일정 추가하기
@mcp.tool()
def add_schedule(time_str: str, title: str) -> str:
    """새로운 일정을 달력에 추가합니다. (예: time_str='09:00', title='회의')"""
    with open(SCHEDULE_DB, "r", encoding="utf-8") as f: data = json.load(f)
    data.append({"time": time_str, "title": title})
    # 시간을 기준으로 정렬해서 다시 저장
    data.sort(key=lambda x: x["time"])
    with open(SCHEDULE_DB, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    return f"완료: [스케줄 - {time_str} {title}] 일정이 달력에 등록되었습니다!"

# 4. 스케줄 툴 - 목록 보기
@mcp.tool()
def list_schedules() -> str:
    """오늘 예약되어 있는 전체 일정을 확인합니다."""
    with open(SCHEDULE_DB, "r", encoding="utf-8") as f: data = json.load(f)
    if not data: return "오늘 일정이 없습니다."
    return "\n".join([f"[{d['time']}] {d['title']}" for d in data])

if __name__ == "__main__":
    print("🚀 [MCP 서버 가동] 시스템 툴(Todo, Schedule) 연결 준비 끝!")
    mcp.run()
