chcp 65001 >nul
@echo off

echo ============================================================
echo  Запуск голосового помощника Джарвис
echo ============================================================
echo.

:: Проверка существования виртуального окружения
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Виртуальное окружение не найдено!
    echo Запустите сначала firstStart.bat
    echo.
    pause
    exit /b 1
)

:: Запуск помощника
.venv\Scripts\python.exe main.py

:: Закрываем окно (все логи в logs/assistant.log)
exit
