@echo off
chcp 65001 >nul
cd /d "%~dp0.."
set ROOT=%CD%
cd /d "%~dp0"

echo ============================================
echo  Knowledge Vault Web exe 빌드 (경량, Whisper 미포함)
echo ============================================
echo.

echo [1/4] 빌드 도구·라이브러리 설치
pip install pyinstaller pyyaml openpyxl pypdf python-pptx olefile python-docx pytesseract Pillow -q

echo [2/4] 소스 복사 (kv / profiles / kv-web)
robocopy "%ROOT%\knowledge-vault\kv" "%~dp0kv" /MIR /XD __pycache__ /NFL /NDL /NJH /NJS /nc /ns /np >nul
robocopy "%ROOT%\knowledge-vault\profiles" "%~dp0profiles" /MIR /NFL /NDL /NJH /NJS /nc /ns /np >nul
robocopy "%ROOT%\kv-web" "%~dp0kv-web" /MIR /XD __pycache__ /NFL /NDL /NJH /NJS /nc /ns /np >nul

echo [3/4] PyInstaller 빌드
pyinstaller --noconfirm --clean KnowledgeVaultWeb.spec

echo [4/4] 결과 확인
if exist "dist\KnowledgeVaultWeb.exe" (
  echo.
  echo === 빌드 완료! ===
  echo   배포 파일: %~dp0dist\KnowledgeVaultWeb.exe
  echo.
  echo [배포 방법]
  echo   1) 빈 폴더에 KnowledgeVaultWeb.exe 복사
  echo   2) 같은 폴더에 key.txt 만들기 (LLM_ENDPOINT / LLM_MODEL / LLM_API_KEY)
  echo   3) exe 더블클릭 - 브라우저가 자동으로 열림 ^(http://localhost:8765^)
  echo   * OCR 쓰려면 PC에 Tesseract 설치 ^(winget install UB-Mannheim.TesseractOCR^)
) else (
  echo.
  echo === 빌드 실패 - 위 로그 확인 ===
  echo   디스크 여유^(2GB+^)·Python 설치 확인 후 재시도
)
pause
