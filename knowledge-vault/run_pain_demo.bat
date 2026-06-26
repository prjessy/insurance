@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo  Pain Point 데모 (index.html 기준)
echo  AS-IS 80분 -^> TO-BE 6분
echo ==========================================
echo.

echo [1] Pain point 목록
python -m kv pain
echo.

echo [2] 상담 전사 -^> 상담기록 + Claude 프롬프트팩
python -m kv counsel --text inbox/notes/상담전사_정수남_샘플.txt --customer 정수남
echo.

echo [3] 제안서 프롬프트팩 (정수남)
python -m kv pack propose 정수남
echo.

echo [4] 안내 문자 프롬프트팩 (정수남)
python -m kv pack message 정수남
echo.

echo [5] 갱신 고객 - Obsidian 대시보드.md (Dataview)
echo     E:\project\work05\대시보드.md
echo.
echo 완료. Obsidian에서 AI작업큐 폴더를 확인하세요.
pause
