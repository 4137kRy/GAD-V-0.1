# text/corrector.py
"""
Модуль исправления опечаток.
"""
from typing import Set, Optional, List, Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)

# Настройки
DEFAULT_MAX_DISTANCE = 8  # Максимальное число ошибок в слове
MIN_WORD_LENGTH = 2  # Слова короче не проверяем
MAX_WORD_LENGTH = 50  # Защита от аномально длинных строк
MIN_SIMILARITY_SCORE = 50  # Минимальный процент схожести
SHORT_WORD_MAX_DISTANCE = 1  # Для коротких слов (≤3 буквы) более строгий порог

# Проверка доступности rapidfuzz
RAPIDFUZZ_AVAILABLE = False
try:
    from rapidfuzz.distance.Levenshtein import distance as levenshtein_distance
    from rapidfuzz.process import extractOne
    from rapidfuzz.fuzz import ratio
    RAPIDFUZZ_AVAILABLE = True
    logger.debug("✅ Модуль 'rapidfuzz' доступен")
except ImportError:
    logger.warning("⚠️ Модуль 'rapidfuzz' не установлен. Исправление опечаток недоступно.")


def correct_word(
    word: str,
    allowed_words: Set[str],
    max_distance: int = DEFAULT_MAX_DISTANCE
) -> Optional[str]:
    """
    Пытается исправить опечатку в слове на основе словаря допустимых слов.

    :param word: Слово для исправления
    :param allowed_words: Множество допустимых слов
    :param max_distance: Максимальное расстояние Левенштейна
    :return: Исправленное слово или исходное
    """
    if not isinstance(word, str) or not word:
        return word

    if not allowed_words or not isinstance(allowed_words, set):
        return word

    # Если слово уже есть в словаре
    if word in allowed_words:
        return word

    # Пропускаем слова неподходящей длины
    word_len = len(word)
    if word_len < MIN_WORD_LENGTH or word_len > MAX_WORD_LENGTH:
        logger.debug(f"Слово '{word}' пропущено (длина: {word_len})")
        return word

    # Для коротких слов (≤3 буквы) используем более строгий порог
    # чтобы избежать ложных срабатываний (что → фото, кто → кот и т.д.)
    if word_len <= 3:
        max_distance = min(max_distance, SHORT_WORD_MAX_DISTANCE)

    # Если rapidfuzz недоступен
    if not RAPIDFUZZ_AVAILABLE:
        return word

    try:
        # Ищем наиболее похожее слово
        result = extractOne(
            word,
            allowed_words,
            scorer=ratio,
            score_cutoff=MIN_SIMILARITY_SCORE
        )

        if not result:
            return word

        candidate, score, _ = result

        # Проверяем расстояние Левенштейна
        distance = levenshtein_distance(word, candidate)

        if distance <= max_distance:
            logger.debug(f"Исправлено: '{word}' → '{candidate}' (расстояние: {distance})")
            return candidate

        return word

    except Exception as e:
        logger.warning(f"Ошибка при исправлении слова '{word}': {e}")
        return word


def correct_text_tokens(
    tokens: List[str],
    allowed_words: Set[str],
    max_distance: int = DEFAULT_MAX_DISTANCE
) -> List[str]:
    """
    Исправляет опечатки во всех словах списка токенов.

    :param tokens: Список слов для исправления
    :param allowed_words: Множество допустимых слов
    :param max_distance: Максимальное расстояние Левенштейна
    :return: Список исправленных слов
    """
    if not tokens or not allowed_words:
        return tokens

    corrected: List[str] = []
    correction_count = 0

    for word in tokens:
        if not isinstance(word, str):
            corrected.append(str(word) if word is not None else "")
            continue

        fixed = correct_word(word, allowed_words, max_distance)

        if fixed is not None and fixed != word:
            correction_count += 1

        corrected.append(fixed if fixed is not None else word)

    if correction_count > 0:
        logger.info(f"Исправлено {correction_count} из {len(tokens)} слов")

    return corrected
