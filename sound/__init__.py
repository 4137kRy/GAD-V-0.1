# sound/__init__.py
"""
Модуль звуковой обратной связи.
"""
from .player import SoundPlayer
from .manager import SoundManager

__all__ = [
    "SoundPlayer",
    "SoundManager",
]
