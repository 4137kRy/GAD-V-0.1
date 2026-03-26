chcp 65001 >nul
@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  Первый запуск голосового помощника Джарвис
echo ============================================================
echo.

:: Проверка наличия Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден в системе!
    echo Установите Python 3.8+ с официального сайта:
    echo https://www.python.org/downloads/
    echo.
    echo ВАЖНО: При установке отметьте галочку "Add Python to PATH"
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

:: Проверка наличия requirements.txt
if not exist "requirements.txt" (
    echo [ERROR] Файл requirements.txt не найден в корне проекта!
    echo Убедитесь, что вы запускаете скрипт из папки проекта.
    pause
    exit /b 1
)

:: Создание папки models/ если её нет
if not exist "models" (
    echo Создаю папку для моделей распознавания: models\...
    mkdir models >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось создать папку 'models'. Запустите от имени администратора.
        pause
        exit /b 1
    )
    echo [OK] Папка 'models' создана
) else (
    echo [INFO] Папка 'models' уже существует
)

:: Создание .gitkeep для отслеживания пустой папки в Git
if not exist "models\.gitkeep" (
    type nul > models\.gitkeep
    echo [OK] Добавлен файл .gitkeep для отслеживания папки в репозитории
)

:: ============================================================
::  Проверка модели Vosk
:: ============================================================
echo.
echo [INFO] Проверяю модель распознавания речи Vosk...

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
    echo          +-- ...
)

:: ============================================================
::  Проверка и создание commands.json
:: ============================================================
echo.
echo [INFO] Проверяю конфигурационный файл commands.json...

if exist "config/commands.json" (
    echo [OK] commands.json уже существует — пропускаем создание
    echo    [TIP] Если нужно сбросить настройки, удалите commands.json вручную
) else (
    echo [INFO] commands.json не найден — создаю из шаблона...

    if not exist "config\default_commands.json" (
        echo [ERROR] Ошибка: default_commands.json не найден!
        echo    Убедитесь, что файл шаблона находится в папке config/.
        pause
        exit /b 1
    )

    :: Копирование с сохранением кодировки UTF-8
    copy /Y "config\default_commands.json" "config\commands.json" >nul 2>&1

    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось создать commands.json
        echo    Попробуйте запустить от имени администратора
        pause
        exit /b 1
    )

    echo [OK] commands.json успешно создан из default_commands.json
)

:: Создание виртуального окружения
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Создаю виртуальное окружение в папке .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Ошибка при создании виртуального окружения
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано
) else (
    echo [INFO] Виртуальное окружение .venv уже существует — пропускаем создание
)

echo.
echo Устанавливаю зависимости из requirements.txt...
call .venv\Scripts\activate.bat >nul 2>&1
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ошибка при установке зависимостей
    echo Попробуйте:
    echo   1. Запустить от имени администратора
    echo   2. Проверить интернет-соединение
    echo   3. Выполнить вручную: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo [OK] Все зависимости установлены
echo.

:: ============================================================
::  Завершение установки
:: ============================================================
echo ============================================================
echo  Установка завершена!
echo ============================================================
echo.
:: Проверка модели и вывод инструкции
if not exist "models\vosk-model-small-ru-0.22\conf\model.conf" (
    echo [WARNING] ВАЖНО: Модель распознавания речи не найдена!
    echo.
    echo Скачайте модель по ссылке:
    echo    https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    echo.
    echo Распакуйте содержимое АРХИВА в папку:
    echo    models\vosk-model-small-ru-0.22\
    echo.
    echo После этого запустите помощника через start.bat
    echo.
) else (
    echo [OK] Модель Vosk установлена — помощник готов к работе!
    echo.
)

echo Следующие шаги:
echo   - Запустите помощника: double-click на start.bat
echo.
echo [TIP] Совет: Папка .venv автоматически игнорируется в Git (.gitignore)
echo.
pause
