@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================================
echo  Zapusk golosovogo pomoshchnika Dzharvis (Windows 10)
echo ============================================================
echo.

:: ============================================================
::  1. Proverka virtual'nogo okruzheniya
:: ============================================================
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual'noe okruzhenie ne naydeno!
    echo.
    echo Zapustite snachala firstStart.win10.bat
    echo.
    pause
    exit /b 1
)

:: ============================================================
::  2. Proverka modeli Vosk
:: ============================================================
if not exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [WARNING] Model' Vosk ne naydena!
    echo.
    echo Skachayte model':
    echo    https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Raspakuyte v papku: models\vosk-model-small-ru-0.22\
    echo.
    echo Nazhmite Enter for prodolzheniya...
    pause
)

:: ============================================================
::  3. Proverka konfiguratsii
:: ============================================================
if not exist "config\commands.json" (
    echo [ERROR] Fail config\commands.json ne nayden!
    echo.
    echo Zapustite snachala firstStart.win10.bat
    pause
    exit /b 1
)

:: ============================================================
::  4. Sozdanie papki logov yesli net
:: ============================================================
if not exist "logs" (
    mkdir logs >nul 2>&1
)

:: ============================================================
::  5. Zapusk pomoshchnika
:: ============================================================
echo Zapusk golosovogo pomoshchnika...
echo Logi sokhranyayutsya v papke logs\
echo.

call .venv\Scripts\activate.bat >nul 2>&1

:: Zapusk s perenapravleniem vybrosa v nul
.venv\Scripts\python.exe main.py > logs\assistant.log 2>nul

set exit_code=%errorlevel%

if %exit_code% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] Pomoshchnik zavershilsya s oshibkoy (kod: %exit_code%)
    echo ============================================================
    echo.
    echo Poslednie stroki loga:
    echo.
    powershell -Command "Get-Content logs\assistant.log -Tail 20 -Encoding UTF8"
    echo.
    echo Polnyy log: logs\assistant.log
    echo.
    pause
)

exit /b %exit_code%
