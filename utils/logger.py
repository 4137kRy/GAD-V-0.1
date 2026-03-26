# utils/logger.py
"""
Модуль логирования для голосового помощника.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_dir: str = "logs",
    log_name: str = "assistant.log",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> None:
    """
    Настраивает систему логирования с выводом в файл и консоль.

    :param log_dir: Папка для логов
    :param log_name: Имя файла лога
    :param level: Уровень логирования
    :param format_string: Формат сообщений (по умолчанию: %(asctime)s [%(levelname)s] %(message)s)
    """
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(message)s"

    # Создаём папку для логов
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Создаём файловый хендлер с UTF-8 кодировкой
    file_handler = logging.FileHandler(log_path / log_name, encoding="utf-8-sig")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(format_string))

    # Создаём консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(format_string))

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Получает логгер по имени.

    :param name: Имя логгера (обычно __name__ модуля)
    :return: Логгер
    """
    return logging.getLogger(name)
