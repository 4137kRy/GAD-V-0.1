# text/__init__.py
"""
Модуль обработки текста.
"""
from .normalizer import normalize_text
from .corrector import correct_word, correct_text_tokens, RAPIDFUZZ_AVAILABLE
from .vocabulary import (
    build_allowed_words,
    build_confirmation_word_sets,
    is_confirmation_phrase
)

__all__ = [
    "normalize_text",
    "correct_word",
    "correct_text_tokens",
    "RAPIDFUZZ_AVAILABLE",
    "build_allowed_words",
    "build_confirmation_word_sets",
    "is_confirmation_phrase",
]
