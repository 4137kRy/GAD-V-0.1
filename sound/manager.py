# sound/manager.py
"""
Менеджер звуковых файлов.
"""
from pathlib import Path
from typing import Optional, Dict, Set

from utils.paths import get_sounds_dir
from utils.logger import get_logger

logger = get_logger(__name__)


class SoundManager:
    """
    Управление звуковыми файлами: поиск, кэширование, валидация.
    """

    SUPPORTED_EXTENSIONS = {".wav"}

    def __init__(self, sounds_dir: Optional[str] = None):
        """
        :param sounds_dir: Путь к папке со звуками (по умолчанию sounds/)
        """
        self.sounds_dir = Path(sounds_dir) if sounds_dir else get_sounds_dir()
        self._cache: Dict[str, Path] = {}
        self._available_sounds: Set[str] = set()

    def get_sound_path(self, sound_name: str) -> Optional[Path]:
        """
        Возвращает полный путь к звуковому файлу.

        :param sound_name: Имя файла
        :return: Path к файлу или None
        """
        # Проверяем кэш
        if sound_name in self._cache:
            return self._cache[sound_name]

        # Проверяем относительный путь
        sound_path = self.sounds_dir / sound_name
        if sound_path.exists():
            self._cache[sound_name] = sound_path
            return sound_path

        # Проверяем как абсолютный путь
        abs_path = Path(sound_name)
        if abs_path.is_absolute() and abs_path.exists():
            self._cache[sound_name] = abs_path
            return abs_path

        logger.warning(f"🔊 Звук не найден: {sound_name}")
        return None

    def has_sound(self, sound_name: str) -> bool:
        """
        Проверяет наличие звукового файла.

        :param sound_name: Имя файла
        :return: True если файл существует
        """
        return self.get_sound_path(sound_name) is not None

    def scan_sounds(self) -> Set[str]:
        """
        Сканирует папку и возвращает имена доступных WAV-файлов.

        :return: Множество имён файлов
        """
        self._available_sounds = set()

        if not self.sounds_dir.exists():
            logger.warning(f"Папка sounds не найдена: {self.sounds_dir}")
            return self._available_sounds

        for file_path in self.sounds_dir.iterdir():
            if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self._available_sounds.add(file_path.name)

        logger.info(f"🔊 Найдено звуков: {len(self._available_sounds)}")
        return self._available_sounds

    def get_available_sounds(self) -> Set[str]:
        """
        Возвращает множество доступных звуков.

        :return: Множество имён
        """
        if not self._available_sounds:
            self.scan_sounds()
        return self._available_sounds

    def clear_cache(self) -> None:
        """
        Очищает кэш путей.
        """
        self._cache.clear()
