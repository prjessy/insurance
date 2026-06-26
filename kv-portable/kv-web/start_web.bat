@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Knowledge Vault Web (Python 설치 불필요)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server.ps1"
