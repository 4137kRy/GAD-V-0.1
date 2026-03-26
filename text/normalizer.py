# text/normalizer.py
"""
Модуль нормализации текста.
"""
import re
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)

# Разрешённые символы: кириллица, латиница, цифры, пробелы
ALLOWED_CHARS_PATTERN = re.compile(r'[^\w\s]', re.IGNORECASE)

# Поиск нескольких пробелов подряд
MULTIPLE_SPACES_PATTERN = re.compile(r'\s+')


def normalize_text(text: Any) -> str:
    """
    Приводит текст к единому виду для надёжного распознавания.

    :param text: Исходный текст (любой тип)
    :return: Нормализованная строка
    """
    # Обрабатываем None и пустые значения
    if text is None:
        return ""

    # Преобразуем не-строки в строку
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            logger.warning(f"Не удалось преобразовать текст в строку: {type(text)}")
            return ""

    # Проверяем на пустую строку после обрезки пробелов
    if not text.strip():
        return ""

    try:
        # Переводим в нижний регистр для единообразия
        text = text.lower()

        # Удаляем спецсимволы и пунктуацию
        text = ALLOWED_CHARS_PATTERN.sub(' ', text)

        # Заменяем множественные пробелы на один
        text = MULTIPLE_SPACES_PATTERN.sub(' ', text)

        # Убираем пробелы по краям строки
        text = text.strip()

        logger.debug(f"Нормализация: '{text[:50]}...' → '{text[:50]}...'")
        return text

    except Exception as e:
        logger.error(f"Ошибка нормализации текста: {e}")
        return ""
