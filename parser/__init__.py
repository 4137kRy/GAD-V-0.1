# parser/__init__.py
"""
Модуль парсинга команд.
"""
from .engine import find_command, check_requires_confirmation
from .multiword import find_multiword_command
from .token import find_token_command

__all__ = [
    "find_command",
    "check_requires_confirmation",
    "find_multiword_command",
    "find_token_command",
]
