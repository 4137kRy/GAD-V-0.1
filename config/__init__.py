# config/__init__.py
"""
Модуль работы с конфигурацией.
"""
from .loader import load_config, load_settings, get_microphone_id
from .normalizer import normalize_config, normalize_phrase

__all__ = [
    "load_config",
    "load_settings",
    "get_microphone_id",
    "normalize_config",
    "normalize_phrase",
]
