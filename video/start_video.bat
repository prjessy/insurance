@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [1] 브라우저 소개 영상 (자동 재생, 약 43초)
start "" "%~dp0promo.html"
echo.
echo    전체화면(F11) + 화면 녹화(Win+G)로 MP4 저장 가능
echo.
echo [2] MP4 자동 생성...
pip install imageio imageio-ffmpeg pillow -q 2>nul
python make_video.py
for %%F in ("%~dp0보험영업AI도우미_소개.mp4" "F:\보험영업AI도우미_소개.mp4" "%USERPROFILE%\Videos\보험영업AI도우미_소개.mp4") do (
  if exist %%F (
    echo.
    echo MP4 생성 완료: %%F
    start "" %%F
    goto :done
  )
)
:done
pause
