@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================================
echo  Установка голосового помощника Джарвис (Windows 10)
echo ============================================================
echo.

:: ============================================================
::  1. Проверка Python
:: ============================================================
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден в системе!
    echo.
    echo Установите Python 3.8+ с официального сайта:
    echo https://www.python.org/downloads/
    echo.
    echo ВАЖНО: При установке отметьте галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Определение версии Python
for /f "tokens=2 delims=. " %%a in ('python --version 2^>^&1') do set py_major=%%a
for /f "tokens=3 delims=. " %%a in ('python --version 2^>^&1') do set py_minor=%%a

:: Проверка версии (требуется 3.8+)
if !py_major! LSS 3 (
    echo [ERROR] Требуется Python 3.8 или новее. Установлена версия !py_major!.!py_minor!
    pause
    exit /b 1
)
if !py_major! EQU 3 if !py_minor! LSS 8 (
    echo [ERROR] Требуется Python 3.8 или новее. Установлена версия 3.!py_minor!
    pause
    exit /b 1
)

echo [OK] Обнаружен Python !py_major!.!py_minor!
echo.

:: ============================================================
::  2. Проверка requirements.txt
:: ============================================================
if not exist "requirements.txt" (
    echo [ERROR] Файл requirements.txt не найден в корне проекта!
    pause
    exit /b 1
)

:: ============================================================
::  3. Создание необходимых папок
:: ============================================================
echo Создаю необходимые папки...

if not exist "models" (
    mkdir models >nul 2>&1
    echo [OK] Папка 'models' создана
) else (
    echo [INFO] Папка 'models' уже существует
)

if not exist "models\.gitkeep" (
    type nul > models\.gitkeep
)

if not exist "logs" (
    mkdir logs >nul 2>&1
    echo [OK] Папка 'logs' создана
) else (
    echo [INFO] Папка 'logs' уже существует
)

if not exist "sounds" (
    mkdir sounds >nul 2>&1
    echo [OK] Папка 'sounds' создана
) else (
    echo [INFO] Папка 'sounds' уже существует
)

echo.

:: ============================================================
::  4. Проверка модели Vosk
:: ============================================================
echo [INFO] Проверяю модель распознавания речи Vosk...
echo.

if exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [OK] Модель Vosk уже установлена
) else (
    echo [WARNING] Модель НЕ найдена в папке models\
    echo.
    echo Скачайте модель по ссылке:
    echo    https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Распакуйте содержимое АРХИВА в папку:
    echo    models\vosk-model-small-ru-0.22\
    echo.
    echo    Правильная структура:
    echo      models\
    echo      +-- vosk-model-small-ru-0.22\
    echo          +-- am\
    echo          +-- conf\
    echo          +-- graph\
    echo.
)

:: ============================================================
::  5. Создание commands.json
:: ============================================================
echo.
echo [INFO] Проверяю конфигурационный файл commands.json...

if exist "config\commands.json" (
    echo [OK] commands.json уже существует
) else (
    if not exist "config\default_commands.json" (
        echo [ERROR] Ошибка: default_commands.json не найден!
        pause
        exit /b 1
    )

    copy /Y "config\default_commands.json" "config\commands.json" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось создать commands.json
        pause
        exit /b 1
    )
    echo [OK] commands.json создан из default_commands.json
)

:: ============================================================
::  6. Создание виртуального окружения
:: ============================================================
echo.
if not exist ".venv\Scripts\python.exe" (
    echo Создаю виртуальное окружение в папке .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Ошибка при создании виртуального окружения
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано
) else (
    echo [INFO] Виртуальное окружение уже существует
)

:: ============================================================
::  7. Установка зависимостей
:: ============================================================
echo.
echo Устанавливаю зависимости из requirements.txt...
echo Это может занять несколько минут...
echo.

call .venv\Scripts\activate.bat >nul 2>&1

:: Обновление pip
python -m pip install --upgrade pip

:: Установка зависимостей
pip install -r requirements.txt
set pip_result=%errorlevel%

if %pip_result% neq 0 (
    echo.
    echo [WARNING] Не удалось установить некоторые зависимости через pip
    echo [INFO] Попытка установки PyAudio через pipwin...
    echo.
    pip install pipwin
    pipwin install pyaudio
    echo [OK] PyAudio установлен через pipwin
)

echo.
echo [OK] Все зависимости установлены
echo.

:: ============================================================
::  8. Завершение установки
:: ============================================================
echo ============================================================
echo  Установка завершена!
echo ============================================================
echo.

if not exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [WARNING] ВАЖНО: Модель распознавания речи не найдена!
    echo.
    echo Скачайте модель по ссылке:
    echo    https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Распакуйте в папку: models\vosk-model-small-ru-0.22\
    echo.
) else (
    echo [OK] Модель Vosk установлена — помощник готов к работе!
    echo.
)

echo Следующие шаги:
echo   1. Убедитесь, что модель Vosk скачана и распакована
echo   2. Запустите помощника через start.win10.bat
echo.
echo [TIP] Для работы медиа-команд может потребоваться запуск от имени администратора
echo.
pause
