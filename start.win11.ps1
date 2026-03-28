# ==============================================================================
#  start.win11.ps1 - Скрипт запуска для Windows 11
#  Голосовой помощник Джарвис
# ==============================================================================

# Установка UTF-8 кодировки для вывода
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Запуск голосового помощника Джарвис (Windows 11)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================================================
#  1. Проверка виртуального окружения
# ==============================================================================
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Запустите сначала firstStart.win11.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# ==============================================================================
#  2. Проверка модели Vosk
# ==============================================================================
$voskModelPath = "models\vosk-model-small-ru-0.22\conf\model.conf"
if (-not (Test-Path $voskModelPath)) {
    Write-Host "[WARNING] Модель Vosk не найдена!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Скачайте модель:" -ForegroundColor Cyan
    Write-Host "   https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Распакуйте в папку: models\vosk-model-small-ru-0.22\" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Продолжить без модели? (y/n)"
    if ($continue -ne 'y') {
        exit 1
    }
}

# ==============================================================================
#  3. Проверка конфигурации
# ==============================================================================
if (-not (Test-Path "config\commands.json")) {
    Write-Host "[ERROR] Файл config\commands.json не найден!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Запустите сначала firstStart.win11.ps1" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# ==============================================================================
#  4. Создание папки логов если нет
# ==============================================================================
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

# ==============================================================================
#  5. Запуск помощника
# ==============================================================================
Write-Host "Запуск голосового помощника..." -ForegroundColor Green
Write-Host "Логи сохраняются в папке logs\" -ForegroundColor Gray
Write-Host ""

# Активация виртуального окружения
& ".venv\Scripts\Activate.ps1"

# Запуск с перенаправлением вывода в лог
try {
    & ".venv\Scripts\python.exe" main.py 2>&1 | Tee-Object -FilePath "logs\assistant.log" -Append
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host ""
    Write-Host "[ERROR] Произошла ошибка при запуске: $_" -ForegroundColor Red
    $exitCode = 1
}

# ==============================================================================
#  6. Обработка результата
# ==============================================================================
if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host " [ERROR] Помощник завершился с ошибкой (код: $exitCode)" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Последние строки лога:" -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path "logs\assistant.log") {
        Get-Content "logs\assistant.log" -Tail 20 -Encoding UTF8
    }
    
    Write-Host ""
    Write-Host "Полный лог: logs\assistant.log" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Нажмите Enter для завершения"
}

exit $exitCode
