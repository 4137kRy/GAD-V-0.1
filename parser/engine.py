# parser/engine.py
"""
Основной движок парсинга команд.
"""
from typing import Optional, Dict, Any

from .multiword import find_multiword_command
from .token import find_token_command
from utils.logger import get_logger

logger = get_logger(__name__)


def check_requires_confirmation(
    identifier_key: str,
    verb_key: str,
    config: Dict[str, Any]
) -> bool:
    """
    Проверяет, требует ли команда подтверждения.

    :param identifier_key: Ключ идентификатора
    :param verb_key: Ключ глагола
    :param config: Словарь конфигурации
    :return: True если требуется подтверждение
    """
    try:
        actions = config.get("actions", {})
        action_def = actions.get(identifier_key, {}).get(verb_key, {})

        if not isinstance(action_def, dict):
            return False

        return action_def.get("requires_confirmation", False)

    except (KeyError, TypeError):
        return False


def find_command(
    normalized_text: str,
    config: Dict[str, Dict],
    window_size: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Основная функция распознавания команды.

    :param normalized_text: Нормализованный текст команды
    :param config: Словарь конфигурации
    :param window_size: Размер окна для поиска токенов
    :return: Словарь {'identifier': str, 'verb': str, 'requires_confirmation': bool} или None
    """
    if not normalized_text or not isinstance(normalized_text, str):
        return None

    if not config or not isinstance(config, dict):
        return None

    # 1. Приоритет: многословные фразы
    multiword_result = find_multiword_command(normalized_text, config)
    if multiword_result:
        identifier_key, verb_key = multiword_result
        requires_confirmation = check_requires_confirmation(
            identifier_key, verb_key, config
        )
        return {
            'identifier': identifier_key,
            'verb': verb_key,
            'requires_confirmation': requires_confirmation
        }

    # 2. Fallback: поиск по токенам
    tokens = normalized_text.split()
    if not tokens:
        return None

    token_result = find_token_command(tokens, config, window_size)
    if token_result:
        identifier_key, verb_key = token_result
        requires_confirmation = check_requires_confirmation(
            identifier_key, verb_key, config
        )
        return {
            'identifier': identifier_key,
            'verb': verb_key,
            'requires_confirmation': requires_confirmation
        }

    return None
