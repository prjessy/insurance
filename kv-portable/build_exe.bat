@echo off
chcp 65001 >nul
cd /d "%~dp0.."
set ROOT=%CD%
cd /d "%~dp0"

echo ============================================
echo  Knowledge Vault Portable 빌드 (폴더형)
echo  필요 공간: 약 2GB 여유
echo ============================================
echo.

pip install -r requirements.txt -q
robocopy "%ROOT%\kv-web" "%~dp0kv-web" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul
robocopy "%ROOT%\knowledge-vault\kv" "%~dp0kv" /E /NFL /NDL /NJH /NJS /nc /ns /np >nul

pyinstaller --noconfirm --clean ^
  --name KnowledgeVault ^
  --onedir ^
  --console ^
  --add-data "kv-web;kv-web" ^
  --add-data "kv;kv" ^
  --hidden-import=faster_whisper ^
  --collect-all faster_whisper ^
  launcher.py

if exist "dist\KnowledgeVault\KnowledgeVault.exe" (
  echo.
  echo 빌드 완료!
  echo   dist\KnowledgeVault\  폴더 전체를 USB에 복사
  echo   KnowledgeVault.exe 더블클릭
  robocopy "dist\KnowledgeVault" "%ROOT%\KnowledgeVault-Portable" /E /NFL /NDL /NJH /NJS /nc /ns /np
  echo   %ROOT%\KnowledgeVault-Portable 에도 복사됨
) else (
  echo.
  echo 빌드 실패 — 디스크 공간 확인 후 재시도
  echo 또는 start.bat 으로 Python 모드 사용
)
pause
