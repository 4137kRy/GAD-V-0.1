# parser/multiword.py
"""
Поиск многословных команд в тексте.
"""
import re
from typing import List, Tuple, Optional, Dict

from utils.logger import get_logger

logger = get_logger(__name__)


def _is_multiword(phrase: str) -> bool:
    """
    Проверяет, состоит ли фраза из более чем одного слова.
    """
    if not phrase or not isinstance(phrase, str):
        return False
    return len(phrase.strip().split()) > 1


def _phrase_in_text(phrase: str, text: str) -> bool:
    """
    Ищет фразу в тексте с учётом границ слов.
    """
    if not phrase or not text:
        return False
    pattern = r'\b' + re.escape(phrase.strip()) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def find_multiword_command(
    normalized_text: str,
    config: Dict[str, Dict]
) -> Optional[Tuple[str, str]]:
    """
    Поиск команд по многословным фразам из конфигурации.

    :param normalized_text: Нормализованный текст команды
    :param config: Словарь конфигурации
    :return: (идентификатор, глагол) или None
    """
    multiword_items: List[Tuple[str, str, str]] = []

    # Собираем многословные глаголы
    verbs_config = config.get("verbs", {})
    if isinstance(verbs_config, dict):
        for verb_key, phrases in verbs_config.items():
            if isinstance(phrases, list):
                for phrase in phrases:
                    if _is_multiword(phrase):
                        multiword_items.append((phrase, "verb", verb_key))

    # Собираем многословные идентификаторы
    identifiers_config = config.get("identifiers", {})
    if isinstance(identifiers_config, dict):
        for ident_key, phrases in identifiers_config.items():
            if isinstance(phrases, list):
                for phrase in phrases:
                    if _is_multiword(phrase):
                        multiword_items.append((phrase, "identifier", ident_key))

    # Сортировка: сначала длинные фразы, затем идентификаторы
    multiword_items.sort(
        key=lambda x: (len(x[0].split()), x[1] == "verb"),
        reverse=True
    )

    # Проверка фраз в тексте
    for phrase, phrase_type, phrase_key in multiword_items:
        if _phrase_in_text(phrase, normalized_text):
            if phrase_type == "verb":
                result = _resolve_verb_command(phrase_key, normalized_text, config)
                if result:
                    return result
            elif phrase_type == "identifier":
                result = _resolve_identifier_command(phrase_key, normalized_text, config)
                if result:
                    return result

    return None


def _resolve_verb_command(
    verb_key: str,
    normalized_text: str,
    config: Dict[str, Dict]
) -> Optional[Tuple[str, str]]:
    """
    Определяет команду, если найден многословный глагол.
    """
    actions_config = config.get("actions", {})

    # Системная команда
    if "system" in actions_config and verb_key in actions_config.get("system", {}):
        return ("system", verb_key)

    # Ищем идентификатор в тексте
    identifiers_config = config.get("identifiers", {})
    for ident_key, ident_phrases in identifiers_config.items():
        if ident_key not in actions_config:
            continue
        if verb_key not in actions_config.get(ident_key, {}):
            continue

        if isinstance(ident_phrases, list):
            for ident_phrase in ident_phrases:
                if _phrase_in_text(ident_phrase, normalized_text):
                    return (ident_key, verb_key)

    # Fallback
    for ident_key in actions_config:
        if verb_key in actions_config.get(ident_key, {}):
            return (ident_key, verb_key)

    return None


def _resolve_identifier_command(
    ident_key: str,
    normalized_text: str,
    config: Dict[str, Dict]
) -> Optional[Tuple[str, str]]:
    """
    Определяет команду, если найден многословный идентификатор.
    """
    actions_config = config.get("actions", {})
    verbs_config = config.get("verbs", {})

    # Ищем глагол в тексте
    for verb_key, verb_phrases in verbs_config.items():
        if verb_key not in actions_config.get(ident_key, {}):
            continue

        if isinstance(verb_phrases, list):
            for verb_phrase in verb_phrases:
                if _phrase_in_text(verb_phrase, normalized_text):
                    return (ident_key, verb_key)

    # Fallback
    for verb_key in actions_config.get(ident_key, {}):
        return (ident_key, verb_key)

    return None
