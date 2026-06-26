@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Knowledge Vault - 전체 파이프라인 실행
pip install -r requirements.txt -q
python create_samples.py 2>nul
python -m kv all --force
python -m kv status
echo.
echo Obsidian 테스트 vault:
echo %~dp0test_obsidian_vault\KnowledgeVault
pause
