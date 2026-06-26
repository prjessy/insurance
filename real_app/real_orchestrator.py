# real_orchestrator.py
# 이 파일은 "Manager AI"와 두 명의 에이전트(Todo, Schedule)가 협동하는 코어 로직입니다.
import json
import time
from real_mcp_server import add_todo, add_schedule, list_todos, list_schedules

class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        print(f"✅ [{self.name}] 가동: 역할({self.role})")

    def execute_with_mcp_tools(self, task: str):
        print(f"\n[{self.name}] 에이전트가 지시사항('{task}')을 분석합니다...")
        time.sleep(1) # AI 사고 시간 시뮬레이션
        
        # 1. 스케줄 에이전트의 로직 (LLM 툴 호출을 모사)
        if "Schedule" in self.name:
            if "9시" in task or "내일" in task:
                print(f"👉 [{self.name}] MCP 도구 <add_schedule>을 공용 허브에서 호출합니다.")
                result = add_schedule("09:00", "기획 회의")
                print(result)
            elif "확인" in task:
                print(f"👉 [{self.name}] MCP 도구 <list_schedules>을 공용 허브에서 호출합니다.")
                print(list_schedules())
                
        # 2. 할 일 에이전트의 로직 (LLM 툴 호출을 모사)
        elif "Todo" in self.name:
            if "자료" in task:
                print(f"👉 [{self.name}] MCP 도구 <add_todo>을 공용 허브에서 호출합니다.")
                result = add_todo("회의 자료 준비하기")
                print(result)
            elif "확인" in task:
                print(f"👉 [{self.name}] MCP 도구 <list_todos>을 공용 허브에서 호출합니다.")
                print(list_todos())
        
        return "완료"

# ---- 메인 실행 흐름 (매니저 AI 중심) ----
def main():
    print("🌟 [다중 에이전트 허브 시작] 🌟\n")
    
    # 1. 든든한 전문가 에이전트 팀 고용
    todo_agent = Agent("Todo AI", "할 일 기록 및 정리")
    schedule_agent = Agent("Schedule AI", "날짜/시간 캘린더 관리")
    
    # 2. 사용자 명령 접수
    user_intent = "내일 9시 회의 스케줄 잡고, 할 일에 '자료 준비' 추가해줘"
    print(f"\n👤 사용자 요청: '{user_intent}'")
    print("--------------------------------------------------")
    
    # 3. 매니저 AI가 라우팅(분배)
    print("👑 [매니저 AI] 작업을 분석하여 전문가들에게 동시 분배합니다.")
    print("--------------------------------------------------")
    
    # 실제로는 이 부분을 병렬(Async)로 실행하여 시간을 2배로 단축합니다.
    schedule_agent.execute_with_mcp_tools(user_intent)
    todo_agent.execute_with_mcp_tools(user_intent)
    
    print("\n--------------------------------------------------")
    print("👑 [매니저 AI] 전체 결과 보고서")
    print("\n[현재 저장된 스케줄 DB 상황]")
    schedule_agent.execute_with_mcp_tools("지금 내 일정 다 확인해봐")
    print("\n[현재 저장된 할 일 DB 상황]")
    todo_agent.execute_with_mcp_tools("지금 내 할일 목록 확인해봐")

if __name__ == "__main__":
    main()
