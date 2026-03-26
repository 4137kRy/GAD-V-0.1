# utils/paths.py
"""
Модуль работы с путями проекта.
"""
import re
from pathlib import Path
from typing import Optional


# Максимальная длина пути
MAX_PATH_LENGTH = 500

# Допустимые символы в пути (Windows + Linux + macOS)
ALLOWED_PATH_PATTERN = re.compile(r'^[\w\\/:.\- ]+$')


def get_project_root() -> Path:
    """
    Возвращает корневую папку проекта.

    :return: Path к корню проекта
    """
    return Path(__file__).parent.parent


def get_absolute_path(path_str: str) -> Path:
    """
    Преобразует строку пути в абсолютный Path.

    :param path_str: Строка пути
    :return: Абсолютный Path
    """
    path = Path(path_str)
    if not path.is_absolute():
        path = get_project_root() / path
    return path


def validate_path(path_str: str, max_length: int = MAX_PATH_LENGTH) -> tuple[bool, str]:
    """
    Проверяет корректность пути.

    :param path_str: Строка пути для проверки
    :param max_length: Максимальная длина пути
    :return: (is_valid, error_message)
    """
    if not path_str or not isinstance(path_str, str):
        return (False, "Путь не указан")

    if len(path_str) > max_length:
        return (False, f"Путь слишком длинный: {len(path_str)} символов (макс. {max_length})")

    if not ALLOWED_PATH_PATTERN.match(path_str):
        return (False, f"Подозрительный путь (недопустимые символы): {path_str}")

    return (True, "")


def get_sounds_dir() -> Path:
    """
    Возвращает путь к папке со звуками.

    :return: Path к sounds/
    """
    return get_project_root() / "sounds"


def get_models_dir() -> Path:
    """
    Возвращает путь к папке с моделями.

    :return: Path к models/
    """
    return get_project_root() / "models"


def get_config_path(config_name: str = "commands.json") -> Path:
    """
    Возвращает путь к файлу конфигурации.

    :param config_name: Имя файла конфигурации
    :return: Path к конфигу
    """
    return get_project_root() / "config" / config_name
