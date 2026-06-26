@echo off
cd /d "%~dp0real_app"
echo Installing dependencies...
pip install -r requirements.txt -q
echo.
echo Starting AI Architecture Automation Server...
echo Open http://localhost:8080 in your browser
echo Add ?autoplay=1 for automatic 4-mode demo
echo.
python api_server.py
