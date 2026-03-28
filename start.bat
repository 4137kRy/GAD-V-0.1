@echo off
chcp 65001 >nul

echo ============================================================
echo  Zapusk golosovogo pomoshchnika Dzharvis
echo ============================================================
echo.

:: Proverka sushchestvovaniya virtual'nogo okruzheniya
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual'noe okruzhenie ne naydeno!
    echo Zapustite snachala firstStart.bat
    echo.
    pause
    exit /b 1
)

:: Zapusk pomoshchnika
.venv\Scripts\python.exe main.py

:: Zakryvaem okno (vse logi v logs/assistant.log)
exit
