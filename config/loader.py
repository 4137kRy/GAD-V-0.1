# config/loader.py
"""
Модуль загрузки и валидации конфигурации.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import get_logger
from utils.paths import get_config_path, get_project_root
from utils.validators import validate_config_structure

logger = get_logger(__name__)

REQUIRED_SECTIONS = {"activation_phrases", "identifiers", "verbs", "actions"}
OPTIONAL_SECTIONS = {"confirmation_phrases"}
ENCODING = "utf-8"


def load_config(config_path: str = "commands.json") -> Dict[str, Any]:
    """
    Загружает JSON конфигурации.

    :param config_path: Путь к файлу конфигурации (относительно config/)
    :return: Словарь конфигурации
    :raises FileNotFoundError: Если файл не найден
    :raises ValueError: Если конфигурация некорректна
    :raises json.JSONDecodeError: Если JSON невалиден
    """
    # Если путь содержит 'config/' — используем как есть, иначе добавляем
    if Path(config_path).parts[0:1] == ('config',):
        path = Path(config_path)
        if not path.is_absolute():
            path = get_project_root() / path
    else:
        path = get_config_path(config_path)

    if not path.exists():
        logger.error(f"❌ Файл конфигурации не найден: {path.absolute()}")
        raise FileNotFoundError(f"Отсутствует конфигурационный файл: {config_path}")

    try:
        with open(path, "r", encoding=ENCODING) as f:
            config = json.load(f)
        logger.debug(f"✅ JSON загружен: {path}")
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON: {e}")
        raise
    except UnicodeDecodeError as e:
        logger.error(f"❌ Ошибка кодировки файла: {e}")
        raise

    # Проверка обязательных разделов
    config_keys = set(config.keys())
    missing_sections = REQUIRED_SECTIONS - config_keys

    if missing_sections:
        error_msg = f"Отсутствуют обязательные секции: {missing_sections}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)

    logger.info(f"✅ Все обязательные секции найдены: {REQUIRED_SECTIONS}")

    # Валидация структуры
    is_valid, errors = validate_config_structure(config)
    if not is_valid:
        for error in errors:
            logger.error(f"❌ {error}")
        raise ValueError("Конфигурация не прошла валидацию")

    return config


def load_settings(settings_path: str = "settings.json") -> Dict[str, Any]:
    """
    Загружает файл настроек (settings.json).

    :param settings_path: Путь к файлу настроек (относительно config/)
    :return: Словарь настроек
    """
    path = get_config_path(settings_path)

    if not path.exists():
        logger.warning(f"⚠️ Файл настроек не найден: {path}, используются значения по умолчанию")
        return {
            "microphone_id": None,
            "vad_threshold": 0.05,
            "activation_timeout": 300,
            "active_timeout": 60
        }

    try:
        with open(path, "r", encoding=ENCODING) as f:
            settings = json.load(f)
        logger.info(f"✅ Настройки загружены: {path}")
        return settings
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON настроек: {e}")
        return {
            "microphone_id": None,
            "vad_threshold": 0.05,
            "activation_timeout": 300,
            "active_timeout": 60
        }
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки настроек: {e}")
        return {
            "microphone_id": None,
            "vad_threshold": 0.05,
            "activation_timeout": 300,
            "active_timeout": 60
        }


def get_microphone_id(settings: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Получает ID микрофона из настроек.

    :param settings: Словарь настроек (если None, загружается из settings.json)
    :return: ID микрофона или None (автовыбор)
    """
    if settings is None:
        settings = load_settings()
    
    mic_id = settings.get("microphone_id")
    
    if mic_id is not None:
        try:
            return int(mic_id)
        except (ValueError, TypeError):
            logger.warning(f"⚠️ Неверный формат microphone_id: {mic_id}, используется автовыбор")
            return None
    return None
