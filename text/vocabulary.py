# text/vocabulary.py
"""
Модуль работы со словарями и фразами.
"""
from typing import Set, Dict, Any, Tuple

from .normalizer import normalize_text
from utils.logger import get_logger

logger = get_logger(__name__)

MIN_WORD_LENGTH = 2


def build_allowed_words(config: Dict[str, Any]) -> Set[str]:
    """
    Собирает все слова из конфигурации для использования в коррекции опечаток.

    :param config: Словарь конфигурации
    :return: Множество допустимых слов
    """
    words: Set[str] = set()

    if not isinstance(config, dict):
        return words

    try:
        # Фразы активации
        for phrase in config.get("activation_phrases", []):
            if isinstance(phrase, str):
                words.update(normalize_text(phrase).split())

        # Идентификаторы
        for ident_list in config.get("identifiers", {}).values():
            if isinstance(ident_list, list):
                for ident in ident_list:
                    if isinstance(ident, str):
                        words.update(normalize_text(ident).split())

        # Глаголы
        for verb_list in config.get("verbs", {}).values():
            if isinstance(verb_list, list):
                for verb in verb_list:
                    if isinstance(verb, str):
                        words.update(normalize_text(verb).split())

        # Фразы подтверждения
        confirmation_phrases = config.get("confirmation_phrases", {})
        if isinstance(confirmation_phrases, dict):
            for phrase in confirmation_phrases.get("confirm", []):
                if isinstance(phrase, str):
                    words.update(normalize_text(phrase).split())
            for phrase in confirmation_phrases.get("cancel", []):
                if isinstance(phrase, str):
                    words.update(normalize_text(phrase).split())

        # Фильтруем короткие слова
        words = {w for w in words if len(w) >= MIN_WORD_LENGTH}

        logger.debug(f"Собрано {len(words)} допустимых слов")

    except Exception as e:
        logger.error(f"Ошибка при сборе допустимых слов: {e}")

    return words


def build_confirmation_word_sets(
    config: Dict[str, Any]
) -> Tuple[Set[str], Set[str]]:
    """
    Создаёт множества слов подтверждения и отмены из конфигурации.

    :param config: Словарь конфигурации
    :return: (confirm_words, cancel_words)
    """
    confirm_words: Set[str] = set()
    cancel_words: Set[str] = set()

    if not isinstance(config, dict):
        return (confirm_words, cancel_words)

    confirmation_phrases = config.get("confirmation_phrases", {})

    if isinstance(confirmation_phrases, dict):
        for phrase in confirmation_phrases.get("confirm", []):
            if isinstance(phrase, str):
                confirm_words.update(normalize_text(phrase).split())
        for phrase in confirmation_phrases.get("cancel", []):
            if isinstance(phrase, str):
                cancel_words.update(normalize_text(phrase).split())

    # Фильтруем короткие слова
    confirm_words = {w for w in confirm_words if len(w) >= MIN_WORD_LENGTH}
    cancel_words = {w for w in cancel_words if len(w) >= MIN_WORD_LENGTH}

    logger.debug(f"Фразы подтверждения: {confirm_words}, отмены: {cancel_words}")

    return (confirm_words, cancel_words)


def is_confirmation_phrase(
    normalized_text: str,
    confirm_words: Set[str],
    cancel_words: Set[str]
) -> Tuple[bool, bool]:
    """
    Проверяет, является ли текст фразой подтверждения или отмены.

    :param normalized_text: Нормализованный текст
    :param confirm_words: Слова подтверждения
    :param cancel_words: Слова отмены
    :return: (is_confirm, is_cancel)
    """
    if not normalized_text:
        return (False, False)

    tokens = normalized_text.split()
    is_confirm = any(word in confirm_words for word in tokens)
    is_cancel = any(word in cancel_words for word in tokens)

    return (is_confirm, is_cancel)
