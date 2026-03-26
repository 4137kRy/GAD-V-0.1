# core/session.py
"""
Менеджер сессии и таймауты.
"""
import time
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# Настройки временных интервалов (секунды)
TIMEOUT_WAITING = 12  # Время ожидания активационной фразы в режиме сна
ACTIVE_TIMEOUT = 18  # Время жизни активного режима без команд
ACTIVE_LISTEN_TIMEOUT = 12  # Время на распознавание одной команды в активном режиме
CONFIRMATION_TIMEOUT = 6   # Время на ответ при подтверждении
MAX_LISTEN_DURATION = 20   # Максимальная длительность записи (ограничение)


class SessionManager:
    """
    Управляет таймаутами сессии.
    """

    def __init__(
        self,
        timeout_waiting: int = TIMEOUT_WAITING,
        active_timeout: int = ACTIVE_TIMEOUT,
        active_listen_timeout: int = ACTIVE_LISTEN_TIMEOUT,
        confirmation_timeout: int = CONFIRMATION_TIMEOUT,
        max_listen_duration: int = MAX_LISTEN_DURATION
    ):
        """
        :param timeout_waiting: Таймаут ожидания активации
        :param active_timeout: Таймаут бездействия в активном режиме
        :param active_listen_timeout: Таймаут прослушивания команды
        :param confirmation_timeout: Таймаут подтверждения
        :param max_listen_duration: Максимальная длительность записи
        """
        self.timeout_waiting = timeout_waiting
        self.active_timeout = active_timeout
        self.active_listen_timeout = active_listen_timeout
        self.confirmation_timeout = confirmation_timeout
        self.max_listen_duration = max_listen_duration

        self._last_command_time: Optional[float] = None

    @property
    def last_command_time(self) -> Optional[float]:
        """Время последней команды."""
        return self._last_command_time

    def update_command_time(self) -> None:
        """Обновляет время последней команды."""
        self._last_command_time = time.time()

    def get_listen_timeout(
        self,
        is_confirmation: bool = False,
        is_waiting: bool = False
    ) -> int:
        """
        Возвращает таймаут прослушивания.

        :param is_confirmation: Режим ожидания подтверждения
        :param is_waiting: Режим ожидания активационной фразы
        :return: Таймаут в секундах
        """
        if is_confirmation:
            return self.confirmation_timeout
        if is_waiting:
            return self.timeout_waiting
        return self.active_listen_timeout

    def get_max_listen_duration(self) -> int:
        """
        Возвращает максимальную длительность записи.

        :return: Максимальная длительность в секундах
        """
        return self.max_listen_duration

    def check_active_timeout(self) -> bool:
        """
        Проверяет, истёк ли таймаут бездействия.

        :return: True если таймаут истёк
        """
        if self._last_command_time is None:
            return False

        elapsed = time.time() - self._last_command_time
        return elapsed > self.active_timeout

    def reset(self) -> None:
        """Сбрасывает таймеры."""
        self._last_command_time = None
        logger.debug("🔄 Таймеры сессии сброшены")
