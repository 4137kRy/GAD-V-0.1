@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================================
echo  Запуск голосового помощника Джарвис (Windows 11)
echo ============================================================
echo.

:: ============================================================
::  1. Проверка виртуального окружения
:: ============================================================
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Виртуальное окружение не найдено!
    echo.
    echo Запустите сначала firstStart.win11.bat
    echo.
    pause
    exit /b 1
)

:: ============================================================
::  2. Проверка модели Vosk
:: ============================================================
if not exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [WARNING] Модель Vosk не найдена!
    echo.
    echo Скачайте модель:
    echo    https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Распакуйте в папку: models\vosk-model-small-ru-0.22\
    echo.
    echo Нажмите Enter для продолжения (может не работать без модели)...
    pause
)

:: ============================================================
::  3. Проверка конфигурации
:: ============================================================
if not exist "config\commands.json" (
    echo [ERROR] Файл config\commands.json не найден!
    echo.
    echo Запустите сначала firstStart.win11.bat
    pause
    exit /b 1
)

:: ============================================================
::  4. Создание папки логов если нет
:: ============================================================
if not exist "logs" (
    mkdir logs >nul 2>&1
)

:: ============================================================
::  5. Запуск помощника
:: ============================================================
echo Запуск голосового помощника...
echo Логи сохраняются в папке logs\
echo.

call .venv\Scripts\activate.bat >nul 2>&1

:: Запуск с перенаправлением вывода в лог
.venv\Scripts\python.exe main.py > logs\assistant.log 2>&1

set exit_code=%errorlevel%

if %exit_code% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] Помощник завершился с ошибкой (код: %exit_code%)
    echo ============================================================
    echo.
    echo Последние строки лога:
    echo.
    powershell -Command "Get-Content logs\assistant.log -Tail 20 -Encoding UTF8"
    echo.
    echo Полный лог: logs\assistant.log
    echo.
    pause
)

exit /b %exit_code%
