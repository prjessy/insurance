@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo  work05 프로젝트 (E:\project\work05)
echo ==========================================
echo.
echo [1] AI Architecture Demo (웹)
echo     start_demo.bat
echo.
echo [2] Knowledge Vault Web (Python 불필요!)  <-- 추천
echo     kv-web\start_web.bat
echo.
echo [3] Knowledge Vault CLI (Python 필요)
echo     knowledge-vault\start.bat
echo.
pause
