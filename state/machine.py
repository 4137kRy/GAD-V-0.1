# state/machine.py
"""
Машина состояний голосового помощника.
"""
from enum import Enum
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class AssistantState(Enum):
    """Состояния ассистента."""
    WAITING = "waiting"       # Ожидание активационной фразы
    ACTIVE = "active"         # Активный режим (приём команд)
    DEACTIVATED = "deactivated"  # Деактивирован (по команде)
    STOPPED = "stopped"       # Остановка (выход из программы)


class StateMachine:
    """
    Управляет состояниями голосового помощника.
    """

    def __init__(self):
        """Инициализирует машину состояний."""
        self._state = AssistantState.WAITING
        logger.info(f"🔄 Начальное состояние: {self._state.value}")

    @property
    def state(self) -> AssistantState:
        """Текущее состояние."""
        return self._state

    @property
    def is_waiting(self) -> bool:
        """Проверяет, находится ли в режиме ожидания."""
        return self._state == AssistantState.WAITING

    @property
    def is_active(self) -> bool:
        """Проверяет, находится ли в активном режиме."""
        return self._state == AssistantState.ACTIVE

    @property
    def is_deactivated(self) -> bool:
        """Проверяет, деактивирован ли ассистент."""
        return self._state == AssistantState.DEACTIVATED

    @property
    def is_stopped(self) -> bool:
        """Проверяет, остановлен ли ассистент."""
        return self._state == AssistantState.STOPPED

    def activate(self) -> None:
        """Переводит в активный режим (после активационной фразы)."""
        if self._state != AssistantState.ACTIVE:
            self._state = AssistantState.ACTIVE
            logger.info("🎯 Активный режим включён")

    def deactivate(self) -> None:
        """Переводит в режим ожидания (по команде или таймауту)."""
        if self._state != AssistantState.WAITING:
            self._state = AssistantState.WAITING
            logger.debug("🔄 Состояние изменено на WAITING")

    def stop(self) -> None:
        """Останавливает ассистента (выход из программы)."""
        self._state = AssistantState.STOPPED
        logger.info("🛑 Помощник остановлен")

    def reactivate(self) -> None:
        """Повторная активация после деактивации."""
        if self._state == AssistantState.DEACTIVATED:
            self._state = AssistantState.WAITING
            logger.info("🔄 Повторная активация после деактивации")

    def transition_to(self, state: AssistantState) -> None:
        """
        Принудительный переход к состоянию.

        :param state: Целевое состояние
        """
        old_state = self._state
        self._state = state
        logger.info(f"🔄 Переход состояния: {old_state.value} → {state.value}")
