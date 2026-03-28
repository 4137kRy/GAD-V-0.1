# core/signals.py
"""
Обработчики сигналов завершения.
"""
import signal
from typing import Callable, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# Флаг завершения работы
shutdown_requested = False


def get_shutdown_flag() -> bool:
    """
    Возвращает флаг завершения работы.

    :return: True если запрошено завершение
    """
    return shutdown_requested


def signal_handler(signum: int, frame) -> None:
    """
    Обработчик сигналов SIGINT и SIGTERM.

    :param signum: Номер сигнала
    :param frame: Фрейм
    """
    global shutdown_requested
    logger.info(f"Получен сигнал {signum}. Завершение работы...")
    shutdown_requested = True


def setup_signal_handlers(handler: Optional[Callable] = None) -> None:
    """
    Устанавливает обработчики сигналов.

    :param handler: Функция-обработчик (по умолчанию signal_handler)
    """
    if handler is None:
        handler = signal_handler

    signal.signal(signal.SIGINT, handler)
    
    # SIGTERM не поддерживается на Windows для пользовательских обработчиков
    import platform
    if platform.system() != "Windows":
        signal.signal(signal.SIGTERM, handler)
    
    logger.debug("✅ Обработчики сигналов установлены")


def reset_shutdown_flag() -> None:
    """Сбрасывает флаг завершения."""
    global shutdown_requested
    shutdown_requested = False
