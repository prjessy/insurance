@echo off
chcp 65001 >nul
cd /d "%~dp0kv-web"
echo ==========================================
echo  보험 영업 AI 도우미 — 웹 버전
echo  Python 설치 불필요
echo ==========================================
echo.
echo  브라우저가 자동으로 열립니다.
echo  주소: http://localhost:8765
echo  종료: 이 창에서 Ctrl+C
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0kv-web\server.ps1"
