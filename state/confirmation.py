# state/confirmation.py
"""
Модуль состояния подтверждения команд.
"""
from typing import Optional, Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)


class ConfirmationState:
    """
    Управляет состоянием ожидания подтверждения команды.
    """

    def __init__(self, max_attempts: int = 3):
        """
        :param max_attempts: Максимальное количество попыток подтверждения
        """
        self.max_attempts = max_attempts
        self.pending = False
        self.command: Optional[Dict[str, Any]] = None
        self.attempts = 0

    def start(self, command: Dict[str, Any]) -> None:
        """
        Начинает ожидание подтверждения для команды.

        :param command: Словарь команды {'identifier': str, 'verb': str}
        """
        self.pending = True
        self.command = command
        self.attempts = 0
        logger.info(f"⚠️ Ожидание подтверждения для: {command['identifier']}/{command['verb']}")

    def reset(self) -> None:
        """Сбрасывает состояние подтверждения."""
        self.pending = False
        self.command = None
        self.attempts = 0

    def increment_attempt(self) -> int:
        """
        Увеличивает счётчик попыток и возвращает новое значение.

        :return: Новое количество попыток
        """
        self.attempts += 1
        return self.attempts

    def is_max_attempts_reached(self) -> bool:
        """
        Проверяет, достигнут ли лимит попыток.

        :return: True если лимит достигнут
        """
        return self.attempts >= self.max_attempts

    def get_command(self) -> Optional[Dict[str, Any]]:
        """
        Возвращает ожидающую подтверждения команду.

        :return: Словарь команды или None
        """
        return self.command
