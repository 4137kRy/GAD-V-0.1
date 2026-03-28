@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================================
echo  Ustanovka golosovogo pomoshchnika Dzharvis (Windows 10)
echo ============================================================
echo.

:: ============================================================
::  1. Proverka Python
:: ============================================================
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python ne nayden v sisteme!
    echo.
    echo Ustanovite Python 3.8+ s ofitsial'nogo sayta:
    echo https://www.python.org/downloads/
    echo.
    echo VAZHNO: Pri ustanovke otmet'te galochku "Add Python to PATH"
    echo.
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

:: ============================================================
::  2. Proverka requirements.txt
:: ============================================================
if not exist "requirements.txt" (
    echo [ERROR] Fail requirements.txt ne nayden v korne proyekta!
    pause
    exit /b 1
)

:: ============================================================
::  3. Sozdaniye neobkhodimykh papok
:: ============================================================
echo Sozdayu neobkhodimyye papki...

if not exist "models" (
    mkdir models >nul 2>&1
    echo [OK] Papka 'models' sozdana
) else (
    echo [INFO] Papka 'models' uzhe sushchestvuyet
)

if not exist "models\.gitkeep" (
    type nul > models\.gitkeep
)

if not exist "logs" (
    mkdir logs >nul 2>&1
    echo [OK] Papka 'logs' sozdana
) else (
    echo [INFO] Papka 'logs' uzhe sushchestvuyet
)

if not exist "sounds" (
    mkdir sounds >nul 2>&1
    echo [OK] Papka 'sounds' sozdana
) else (
    echo [INFO] Papka 'sounds' uzhe sushchestvuyet
)

echo.

:: ============================================================
::  4. Proverka modeli Vosk
:: ============================================================
echo [INFO] Proveryayu model' raspoznavaniya rechi Vosk...
echo.

if exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [OK] Model' Vosk uzhe ustanovlena
) else (
    echo [WARNING] Model' NE naydena v papke models\
    echo.
    echo Skachayte model' po ssylke:
    echo    https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Raspakuyte soderzhimoye ARKHIVA v papku:
    echo    models\vosk-model-small-ru-0.22\
    echo.
    echo    Pravil'naya struktura:
    echo      models\
    echo      +-- vosk-model-small-ru-0.22\
    echo          +-- am\
    echo          +-- conf\
    echo          +-- graph\
    echo.
)

:: ============================================================
::  5. Sozdaniye commands.json
:: ============================================================
echo.
echo [INFO] Proveryayu konfiguratsionnyy fail commands.json...

if exist "config\commands.json" (
    echo [OK] commands.json uzhe sushchestvuyet
) else (
    if not exist "config\default_commands.json" (
        echo [ERROR] Oshibka: default_commands.json ne nayden!
        pause
        exit /b 1
    )

    copy /Y "config\default_commands.json" "config\commands.json" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Ne udalos' sozdat' commands.json
        pause
        exit /b 1
    )
    echo [OK] commands.json sozdan iz default_commands.json
)

:: ============================================================
::  6. Sozdaniye virtual'nogo okruzheniya
:: ============================================================
echo.
if not exist ".venv\Scripts\python.exe" (
    echo Sozdayu virtual'noye okruzheniye v papke .venv...
    python -m venv .venv --clear
    if %errorlevel% neq 0 (
        echo [ERROR] Oshibka pri sozdanii virtual'nogo okruzheniya
        pause
        exit /b 1
    )
    echo [OK] Virtual'noye okruzheniye sozdano
) else (
    echo [INFO] Virtual'noye okruzheniye uzhe sushchestvuyet
)

:: ============================================================
::  7. Ustanovka zavisimostey
:: ============================================================
echo.
echo Ustanavlivayu zavisimosti iz requirements.txt...
echo Eto mozhet zanyat' neskol'ko minut...
echo.

call .venv\Scripts\activate.bat >nul 2>&1

:: Obnovleniye pip
echo [1/3] Obnovleniye pip...
python -m pip install --upgrade pip --quiet

:: Popytka ustanovki cherez pip, pri neudache - cherez pipwin dlya PyAudio
echo [2/3] Ustanovka osnovnykh zavisimostey...
pip install -r requirements.txt --quiet
set pip_result=%errorlevel%

if %pip_result% neq 0 (
    echo.
    echo [WARNING] Ne udalos' ustanovit' nekotoryye zavisimosti cherez pip
    echo [INFO] Popytka ustanovki PyAudio cherez pipwin...
    echo.
    pip install pipwin --quiet
    pipwin install pyaudio --quiet
    echo [OK] PyAudio ustanovlen cherez pipwin
)

:: Ochistka kesha pip
echo [3/3] Ochistka kesha...
pip cache purge >nul 2>&1

echo.
echo [OK] Vse zavisimosti ustanovleny
echo.

:: ============================================================
::  8. Zaversheniye ustanovki
:: ============================================================
echo ============================================================
echo  Ustanovka zavershena!
echo ============================================================
echo.

if not exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [WARNING] VAZHNO: Model' raspoznavaniya rechi ne naydena!
    echo.
    echo Skachayte model' po ssylke:
    echo    https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Raspakuyte v papku: models\vosk-model-small-ru-0.22\
    echo.
) else (
    echo [OK] Model' Vosk ustanovlena — pomoshchnik gotov k rabote!
    echo.
)

echo Sleduyushiye shagi:
echo   1. Ubedites', chto model' Vosk skachana i raspakovana
echo   2. Zapustite pomoshchnika cherez start.win10.bat
echo.
echo [TIP] Dlya raboty media-komand mozhet potrebovat'sya zapusk ot imeni administratora
echo.
pause
