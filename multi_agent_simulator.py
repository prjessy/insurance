# multi_agent_simulator.py
# 이 파일은 "다중 AI 에이전트"들이 어떻게 '하나의 MCP 날씨 서버'를 공유해서 쓰는지
# 개념적으로 보여주는 시뮬레이터입니다.

class AI_Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        # 이 에이전트가 어떤 MCP 단자에 꽂혀있는지를 보관
        self.connected_mcp_tools = {} 

    def connect_tool(self, tool_name, mcp_tool_route):
        """MCP를 통해 받은 권한(도구)을 에이전트에 장착합니다."""
        self.connected_mcp_tools[tool_name] = mcp_tool_route
        print(f"[{self.name}] 역할: {self.role} -> '{tool_name}' MCP 도구 장착 완료!")

    def execute_task(self, task_instruction, *args):
        """본인의 역할에 맞게 도구를 사용하여 일을 처리합니다."""
        print(f"\n--- {self.name} 에이전트 작업 시작 ---")
        print(f"지시사항: {task_instruction}")
        
        # 만약 자기가 가지고 있는 도구 중에 필요한 게 있다면 씁니다.
        if "weather_check" in self.connected_mcp_tools:
            # 이 부분이 실제로 MCP 서버(weather_server.py)에 통신을 보내 날씨를 받아오는 과정입니다.
            tool_func = self.connected_mcp_tools["weather_check"]
            result = tool_func(*args)
            print(f"[{self.name}] 스스로 발견한 정보: {result}")
            return f"보고합시다: 제가 알아본 바에 따르면 {result}입니다."
        else:
            print(f"[{self.name}] 저는 이 일을 할 수 있는 도구(MCP 플러그)가 없습니다.")
            return "실패"

# =========================================================
# 다중 에이전트 시스템 사용 전 vs 사용 후 (개념 비교)
# =========================================================

print("=== 1. 다중 에이전트 + MCP 시스템 설정 ===")

# 1. 역할이 분리된 여러 에이전트 생성
agent_researcher = AI_Agent("조사봇", "웹/데이터 조사 전문가")
agent_planner = AI_Agent("기획봇", "여행 일정 기획 전문가")

# 2. 방금 만든 '날씨 MCP 서버'에서 제공하는 기능이라고 가정 (가상의 함수로 표현)
def mock_mcp_weather_request(location):
    # 실제로는 subprocess 등으로 weather_server.py를 실행하고 JSON-RPC 통신을 주고 받습니다.
    # 여기서는 그 통신 결과를 흉내냅니다.
    weather_db = {"Seoul": "맑음, 20도", "Busan": "비, 15도"}
    return weather_db.get(location, "알 수 없음")

# 3. 조사 에이전트에게만 "날씨 조사" 도구를 꽂아줌 (권한/역할 분리)
agent_researcher.connect_tool("weather_check", mock_mcp_weather_request)
# (기획 에이전트는 날씨를 직접 찾을 권한이 없음)

print("\n=== 2. 실제 업무 실행 (다중 에이전트의 협업) ===")
# 시나리오: 서울로 여행을 가려고 한다. 둘이 협력하라.

# Step A: 조사봇이 자신의 MCP 도구를 사용해 정보를 캡어옵니다.
info = agent_researcher.execute_task("서울의 현재 날씨를 조사해라", "Seoul")

# Step B: 기획봇은 정보 없이 결과만 전달받아 기획이라는 자신의 특기에 집중합니다.
report = agent_planner.execute_task(f"조사бот이 보내온 정보({info})를 바탕으로 서울 여행 일정을 잡아라")
print(f"\n[최종 종합 보고서]\n{agent_planner.name}: 서울 날씨가 맑고 20도라고 하니, 야외 피크닉 위주로 일정을 짰습니다!")
