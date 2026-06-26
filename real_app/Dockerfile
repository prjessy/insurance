# Python Base Image (파이썬이 없는 환경을 위해 가상의 빈 깡통 서버에 파이썬을 자동으로 세팅해주는 명령어)
FROM python:3.11-slim

# 이 컨테이너 안에서 우리가 작업할 기준 폴더 이름 지정
WORKDIR /app

# 파이썬 의존성 목록(mcp 등) 복사해 오기
COPY requirements.txt .

# 명령어 한 줄로 필수 패키지 자동 설치
RUN pip install --no-cache-dir -r requirements.txt

# 우리의 핵심 소스코드 2개 복사
COPY real_mcp_server.py .
COPY real_orchestrator.py .

# 서버가 켜질 때 자동으로 실행할 명령!
CMD ["python", "real_orchestrator.py"]
