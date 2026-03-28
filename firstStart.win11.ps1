# ==============================================================================
#  firstStart.win11.ps1 - Скрипт установки для Windows 11
#  Голосовой помощник Джарвис
# ==============================================================================

# Установка UTF-8 кодировки для вывода
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Установка голосового помощника Джарвис (Windows 11)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================================================
#  1. Проверка Python
# ==============================================================================
Write-Host "[1/8] Проверка Python..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python не найден"
    }
    
    # Извлечение версии
    $versionMatch = $pythonVersion -match 'Python (\d+)\.(\d+)'
    if ($versionMatch) {
        $pyMajor = [int]$Matches[1]
        $pyMinor = [int]$Matches[2]
    } else {
        throw "Не удалось определить версию Python"
    }
    
    if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 8)) {
        throw "Требуется Python 3.8 или новее. Установлена версия $pyMajor.$pyMinor"
    }
    
    Write-Host "[OK] Обнаружен Python $pyMajor.$pyMinor" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Установите Python 3.8+ с официального сайта:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "ВАЖНО: При установке отметьте галочку 'Add Python to PATH'" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# ==============================================================================
#  2. Проверка requirements.txt
# ==============================================================================
Write-Host ""
Write-Host "[2/8] Проверка requirements.txt..." -ForegroundColor Yellow

if (-not (Test-Path "requirements.txt")) {
    Write-Host "[ERROR] Файл requirements.txt не найден!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "[OK] requirements.txt найден" -ForegroundColor Green

# ==============================================================================
#  3. Создание необходимых папок
# ==============================================================================
Write-Host ""
Write-Host "[3/8] Создание необходимых папок..." -ForegroundColor Yellow

$folders = @("models", "logs", "sounds")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "[OK] Папка '$folder' создана" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Папка '$folder' уже существует" -ForegroundColor Gray
    }
}

# Создание .gitkeep для models
if (-not (Test-Path "models\.gitkeep")) {
    New-Item -ItemType File -Path "models\.gitkeep" -Force | Out-Null
}

# ==============================================================================
#  4. Проверка модели Vosk
# ==============================================================================
Write-Host ""
Write-Host "[4/8] Проверка модели Vosk..." -ForegroundColor Yellow

$voskModelPath = "models\vosk-model-small-ru-0.22\conf\model.conf"
if (Test-Path $voskModelPath) {
    Write-Host "[OK] Модель Vosk уже установлена" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Модель НЕ найдена в папке models\" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Скачайте модель по ссылке:" -ForegroundColor Cyan
    Write-Host "   https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Распакуйте содержимое АРХИВА в папку:" -ForegroundColor Yellow
    Write-Host "   models\vosk-model-small-ru-0.22\" -ForegroundColor Yellow
    Write-Host ""
}

# ==============================================================================
#  5. Создание commands.json
# ==============================================================================
Write-Host ""
Write-Host "[5/8] Проверка конфигурационного файла..." -ForegroundColor Yellow

if (Test-Path "config\commands.json") {
    Write-Host "[OK] commands.json уже существует" -ForegroundColor Green
} else {
    if (-not (Test-Path "config\default_commands.json")) {
        Write-Host "[ERROR] default_commands.json не найден!" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    
    Copy-Item "config\default_commands.json" "config\commands.json" -Force
    Write-Host "[OK] commands.json создан из default_commands.json" -ForegroundColor Green
}

# ==============================================================================
#  6. Создание виртуального окружения
# ==============================================================================
Write-Host ""
Write-Host "[6/8] Создание виртуального окружения..." -ForegroundColor Yellow

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Создание виртуального окружения в папке .venv..." -ForegroundColor Gray
    python -m venv .venv --clear
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Ошибка при создании виртуального окружения" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    Write-Host "[OK] Виртуальное окружение создано" -ForegroundColor Green
} else {
    Write-Host "[INFO] Виртуальное окружение уже существует" -ForegroundColor Gray
}

# ==============================================================================
#  7. Установка зависимостей
# ==============================================================================
Write-Host ""
Write-Host "[7/8] Установка зависимостей..." -ForegroundColor Yellow
Write-Host "Это может занять несколько минут..." -ForegroundColor Gray
Write-Host ""

# Активация виртуального окружения
& ".venv\Scripts\Activate.ps1"

Write-Host "[1/3] Обновление pip..." -ForegroundColor Gray
python -m pip install --upgrade pip --quiet

Write-Host "[2/3] Установка основных зависимостей..." -ForegroundColor Gray
pip install -r requirements.txt --quiet
$installResult = $LASTEXITCODE

if ($installResult -ne 0) {
    Write-Host ""
    Write-Host "[WARNING] Не удалось установить некоторые зависимости через pip" -ForegroundColor Yellow
    Write-Host "[INFO] Попытка установки PyAudio через pipwin..." -ForegroundColor Cyan
    Write-Host ""
    
    pip install pipwin --quiet
    pipwin install pyaudio --quiet
    
    Write-Host "[OK] PyAudio установлен через pipwin" -ForegroundColor Green
}

Write-Host "[3/3] Очистка кэша..." -ForegroundColor Gray
pip cache purge --quiet 2>$null

Write-Host ""
Write-Host "[OK] Все зависимости установлены" -ForegroundColor Green

# ==============================================================================
#  8. Завершение установки
# ==============================================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Установка завершена!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $voskModelPath)) {
    Write-Host "[WARNING] ВАЖНО: Модель распознавания речи не найдена!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Скачайте модель по ссылке:" -ForegroundColor Cyan
    Write-Host "   https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Распакуйте в папку: models\vosk-model-small-ru-0.22\" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[OK] Модель Vosk установлена — помощник готов к работе!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "  1. Убедитесь, что модель Vosk скачана и распакована" -ForegroundColor Gray
Write-Host "  2. Запустите помощника через start.win11.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "[TIP] Для работы медиа-команд может потребоваться запуск от имени администратора" -ForegroundColor Cyan
Write-Host ""

Read-Host "Нажмите Enter для завершения"
