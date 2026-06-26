@echo off
chcp 65001 >nul
cd /d "%~dp0real_app"
echo AI Architecture Demo Server 시작...
pip install -r requirements.txt -q
echo 브라우저: http://localhost:8080
python api_server.py
