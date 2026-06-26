@echo off
chcp 65001 >nul
echo ==========================================
echo  AI 자료 도우미 — 웹 (LLM·프로파일 연동)
echo  주소: http://localhost:8765
echo  종료: 이 창에서 Ctrl+C
echo ==========================================
echo.

where python >nul 2>&1
if %errorlevel%==0 (
  echo [Python 모드] AI 질문·자동답변 사용 가능
  cd /d "%~dp0knowledge-vault"
  python -m kv serve
) else (
  echo [정적 모드] Python 없음 — AI 질문은 비활성, 대시보드/프롬프트만 사용
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0kv-web\server.ps1"
)
