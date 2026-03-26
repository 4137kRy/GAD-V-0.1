# config/normalizer.py
"""
Модуль нормализации конфигурации.
"""
import re
from typing import Any, Dict, List

from utils.logger import get_logger

logger = get_logger(__name__)


def normalize_phrase(phrase: str) -> str:
    """
    Приводит фразу к единому виду.

    :param phrase: Исходная фраза
    :return: Нормализованная фраза
    """
    if not isinstance(phrase, str):
        return ""

    phrase = re.sub(r'[^\w\s]', ' ', phrase.lower())
    phrase = re.sub(r'\s+', ' ', phrase)
    return phrase.strip()


def normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Нормализует текстовые данные конфигурации.

    :param config: Словарь конфигурации
    :return: Нормализованный словарь
    """
    normalized_config: Dict[str, Any] = {}

    # Активационные фразы
    activation_phrases = config.get("activation_phrases", [])
    if isinstance(activation_phrases, list):
        normalized_config["activation_phrases"] = [
            normalize_phrase(p) for p in activation_phrases if p
        ]
        logger.debug(f"✅ Нормализовано {len(normalized_config['activation_phrases'])} активационных фраз")
    else:
        normalized_config["activation_phrases"] = []

    # Идентификаторы
    identifiers = config.get("identifiers", {})
    if isinstance(identifiers, dict):
        normalized_config["identifiers"] = {}
        for key, phrases in identifiers.items():
            if isinstance(phrases, list):
                normalized_config["identifiers"][key] = [
                    normalize_phrase(p) for p in phrases if p
                ]
        logger.debug(f"✅ Нормализовано {len(normalized_config['identifiers'])} идентификаторов")
    else:
        normalized_config["identifiers"] = {}

    # Глаголы
    verbs = config.get("verbs", {})
    if isinstance(verbs, dict):
        normalized_config["verbs"] = {}
        for key, phrases in verbs.items():
            if isinstance(phrases, list):
                normalized_config["verbs"][key] = [
                    normalize_phrase(p) for p in phrases if p
                ]
        logger.debug(f"✅ Нормализовано {len(normalized_config['verbs'])} глаголов")
    else:
        normalized_config["verbs"] = {}

    # Действия (без изменений)
    actions = config.get("actions", {})
    if isinstance(actions, dict):
        normalized_config["actions"] = actions
        logger.debug(f"✅ Скопировано {len(actions)} действий")
    else:
        normalized_config["actions"] = {}

    # Фразы подтверждения (опционально)
    confirmation_phrases = config.get("confirmation_phrases", {})
    if confirmation_phrases and isinstance(confirmation_phrases, dict):
        normalized_confirm = []
        for phrase in confirmation_phrases.get("confirm", []):
            if isinstance(phrase, str):
                normalized_confirm.append(normalize_phrase(phrase))

        normalized_cancel = []
        for phrase in confirmation_phrases.get("cancel", []):
            if isinstance(phrase, str):
                normalized_cancel.append(normalize_phrase(phrase))

        normalized_config["confirmation_phrases"] = {
            "confirm": normalized_confirm,
            "cancel": normalized_cancel
        }
        logger.debug(f"✅ Загружено {len(normalized_confirm)} фраз подтверждения")
        logger.debug(f"✅ Загружено {len(normalized_cancel)} фраз отмены")
    else:
        normalized_config["confirmation_phrases"] = {
            "confirm": [],
            "cancel": []
        }

    return normalized_config
