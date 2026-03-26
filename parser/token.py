# parser/token.py
"""
Поиск команд по токенам (fallback-механизм).
"""
from typing import List, Tuple, Optional, Dict

from utils.logger import get_logger

logger = get_logger(__name__)


def _is_multiword(phrase: str) -> bool:
    """Проверяет, состоит ли фраза из более чем одного слова."""
    if not phrase or not isinstance(phrase, str):
        return False
    return len(phrase.strip().split()) > 1


def _build_word_mapping(
    config_section: Dict[str, List[str]],
    filter_multiword: bool = False
) -> Dict[str, str]:
    """
    Создаёт словарь соответствия: отдельное слово -> ключ конфигурации.
    """
    mapping: Dict[str, str] = {}
    if not isinstance(config_section, dict):
        return mapping

    for key, phrases in config_section.items():
        if not isinstance(phrases, list):
            continue

        for phrase in phrases:
            if not isinstance(phrase, str):
                continue

            if filter_multiword and _is_multiword(phrase):
                continue

            for word in phrase.split():
                word = word.strip()
                if word:
                    mapping[word] = key

    return mapping


def find_token_command(
    tokens: List[str],
    config: Dict[str, Dict],
    window_size: int = 3
) -> Optional[Tuple[str, str]]:
    """
    Fallback-механизм: поиск команды по отдельным словам в окне соседства.

    :param tokens: Список токенов команды
    :param config: Словарь конфигурации
    :param window_size: Размер окна для поиска соседних токенов
    :return: (идентификатор, глагол) или None
    """
    word_to_identifier = _build_word_mapping(
        config.get("identifiers", {}),
        filter_multiword=True
    )
    word_to_verb = _build_word_mapping(
        config.get("verbs", {}),
        filter_multiword=True
    )
    actions_config = config.get("actions", {})

    # 1. Сначала проверяем специальный идентификатор "_any" (команды без явного объекта)
    # Для глаголов типа "найди", "погугли" и т.д. — идентификатор подставляется автоматически
    if "_any" in actions_config:
        for i, token in enumerate(tokens):
            if token in word_to_identifier and word_to_identifier[token] == "_any":
                # Нашли слово из "_any", ищем глагол в том же токене или соседях
                window_start = max(0, i - window_size)
                window_end = min(len(tokens), i + window_size + 1)
                
                for j in range(window_start, window_end):
                    neighbor = tokens[j]
                    if neighbor in word_to_verb:
                        verb_key = word_to_verb[neighbor]
                        if ("_any" in actions_config and 
                                verb_key in actions_config.get("_any", {})):
                            return ("_any", verb_key)

    # 2. Поиск пары (Объект + Действие) в пределах окна
    for i, token in enumerate(tokens):
        if token in word_to_identifier:
            ident_key = word_to_identifier[token]
            # Пропускаем "_any" в основном цикле
            if ident_key == "_any":
                continue
            window_start = max(0, i - window_size)
            window_end = min(len(tokens), i + window_size + 1)

            for j in range(window_start, window_end):
                if j == i:
                    continue
                neighbor = tokens[j]
                if neighbor in word_to_verb:
                    verb_key = word_to_verb[neighbor]
                    if (ident_key in actions_config and
                            verb_key in actions_config.get(ident_key, {})):
                        return (ident_key, verb_key)

    # 3. Поиск системных команд (только Действие) — требует явного системного глагола
    # Системные команды: shutdown, sleep, logout, deactivate, stop_assistant
    # Не должны срабатывать для обычных глаголов типа "выключи", "открой" и т.д.
    system_specific_verbs = {"shutdown", "sleep", "logout", "deactivate", "stop_assistant"}
    
    for token in tokens:
        if token in word_to_verb:
            verb_key = word_to_verb[token]
            # Проверяем, что это именно системный глагол
            if verb_key in system_specific_verbs:
                if ("system" in actions_config and
                        verb_key in actions_config.get("system", {})):
                    return ("system", verb_key)

    return None
