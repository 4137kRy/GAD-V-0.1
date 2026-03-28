@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo  Pervyy zapusk golosovogo pomoshchnika Dzharvis
echo ============================================================
echo.

:: Proverka nalichiya Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python ne nayden v sisteme!
    echo Ustanovite Python 3.8+ s ofitsial'nogo sayta:
    echo https://www.python.org/downloads/
    echo.
    echo VAZHNO: Pri ustanovke otmet'te galochku "Add Python to PATH"
    pause
    exit /b 1
)

:: Opredeleniye versii Python
for /f "tokens=2 delims=. " %%a in ('python --version 2^>^&1 ^| findstr /i "Python"') do set py_major=%%a
for /f "tokens=3 delims=. " %%a in ('python --version 2^>^&1 ^| findstr /i "Python"') do set py_minor=%%a

:: Proverka versii (trebuyetsya 3.8+)
if !py_major! LSS 3 (
    echo [ERROR] Trebuyetsya Python 3.8 ili noveye. Ustanovlena versiya !py_major!.!py_minor!
    pause
    exit /b 1
)
if !py_major! EQU 3 if !py_minor! LSS 8 (
    echo [ERROR] Trebuyetsya Python 3.8 ili noveye. Ustanovlena versiya 3.!py_minor!
    pause
    exit /b 1
)

echo [OK] Obnaruzhen Python !py_major!.!py_minor!
echo.

:: Proverka nalichiya requirements.txt
if not exist "requirements.txt" (
    echo [ERROR] Fail requirements.txt ne nayden!
    pause
    exit /b 1
)

:: Sozdaniye papok
echo Sozdayu papki...
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "sounds" mkdir sounds
echo [OK] Papki sozdany
echo.

:: Proverka modeli Vosk
echo [INFO] Proveryayu model' Vosk...
if not exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [WARNING] Model' Vosk NE naydena!
    echo.
    echo Skachayte model':
    echo https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Raspakuyte v papku: models\vosk-model-small-ru-0.22\
    echo.
) else (
    echo [OK] Model' Vosk ustanovlena
)
echo.

:: Sozdaniye commands.json
if not exist "config\commands.json" (
    if exist "config\default_commands.json" (
        copy /Y "config\default_commands.json" "config\commands.json" >nul 2>&1
        echo [OK] commands.json sozdan
    )
) else (
    echo [OK] commands.json uzhe sushchestvuyet
)
echo.

:: Virtual'noye okruzheniye
if not exist ".venv\Scripts\python.exe" (
    echo Sozdayu virtual'noye okruzheniye...
    python -m venv .venv --clear
    echo [OK] Virtual'noye okruzheniye sozdano
) else (
    echo [INFO] Virtual'noye okruzheniye uzhe sushchestvuyet
)
echo.

:: Ustanovka zavisimostey
echo Ustanavlivayu zavisimosti...
call .venv\Scripts\activate.bat >nul 2>&1
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo [OK] Zavisimosti ustanovleny
echo.

echo ============================================================
echo  Ustanovka zavershena!
echo ============================================================
echo.
echo Sleduyushiye shagi:
echo   1. Skachayte model' Vosk (yesli ne skachany)
echo   2. Zapustite start.bat
echo.
pause
