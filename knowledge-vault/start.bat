@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo  Knowledge Vault  (E:\project\work05)
echo ========================================
echo.
echo [1] inbox 에 파일 넣기
echo     audio\  images\  excel\  notes\
echo.
echo [2] 명령어
echo     run_all.bat         샘플+전체 실행
echo     python -m kv all    수집+정제+동기화
echo     python -m kv watch  자동 감시
echo     python -m kv search "검색어"
echo.
echo [3] Obsidian
echo     test_obsidian_vault\KnowledgeVault
echo.
pip install -r requirements.txt -q
python -m kv status
echo.
pause
