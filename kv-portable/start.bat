@echo off
chcp 65001 >nul
title Knowledge Vault Portable
cd /d "%~dp0"

if exist "KnowledgeVault.exe" (
  start "" "KnowledgeVault.exe"
  exit /b 0
)

echo Python으로 Portable 서버 시작...
where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo [Python 없음]
  echo 1. winget install Python.Python.3.12
  echo 2. 또는 KnowledgeVault-Portable 폴더 사용 (build_exe.bat로 빌드)
  echo 3. 또는 kv-web\start_web.bat (Whisper 없이 웹만)
  pause
  exit /b 1
)

if not exist "kv-web" (
  echo kv-web 없음 — work05\kv-portable 에서 실행하세요
  pause
  exit /b 1
)

set PYTHONPATH=%~dp0;%PYTHONPATH%
pip install fastapi uvicorn python-multipart faster-whisper -q 2>nul
python launcher.py
