# weather_server.py
# 이 파일은 날씨 정보를 제공하는 아주 간단한 'MCP 서버'입니다.
# 어떤 AI 에이전트든 이 서버에 연결(플러그 꽂음)하면 날씨를 알 수 있게 됩니다.
# 실행을 위해서는 mcp 패키지가 필요합니다: pip install mcp

from mcp.server.fastmcp import FastMCP

# 이름이 "Weather"인 새로운 MCP 서버를 생성합니다.
mcp = FastMCP("Weather")

# @mcp.tool 데코레이터를 붙이면, 이 함수는 어떤 AI 에이전트든 가져다 쓸 수 있는 '도구(Tool)'가 됩니다!
@mcp.tool()
def get_weather(location: str) -> str:
    """주어진 지역의 현재 날씨를 알려줍니다."""
    
    # 실제로는 기상청 API 등을 호출하겠지만, 여기서는 샘플로 제공합니다.
    weather_data = {
        "Seoul": "맑음, 20도",
        "Busan": "비, 15도",
        "New York": "구름 많음, 10도"
    }
    
    # 해당 지역의 날씨가 있으면 알려주고, 없으면 모른다고 답합니다.
    return weather_data.get(location, f"{location}의 날씨 정보는 알 수 없습니다.")

if __name__ == "__main__":
    # 서버를 실행합니다. 기본적으로 터미널의 입출력(stdio)을 통해 통신합니다.
    mcp.run()
