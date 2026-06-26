@echo off
chcp 65001 >nul
cd /d "%~dp0"

if exist "KnowledgeVault-Portable\KnowledgeVault.exe" (
  echo Portable EXE 실행...
  start "" "%~dp0KnowledgeVault-Portable\KnowledgeVault.exe"
  exit /b 0
)

if exist "kv-portable\dist\KnowledgeVault\KnowledgeVault.exe" (
  start "" "%~dp0kv-portable\dist\KnowledgeVault\KnowledgeVault.exe"
  exit /b 0
)

if exist "kv-portable\start.bat" (
  echo Python Portable 모드...
  call "%~dp0kv-portable\start.bat"
  exit /b 0
)

echo 웹 전용 모드 (Whisper 없음)...
start "" "%~dp0kv-web\start_web.bat"
