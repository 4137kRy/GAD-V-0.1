# sound/player.py
"""
Модуль воспроизведения звуковых файлов.
"""
import os
import subprocess
import threading
from pathlib import Path
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class SoundPlayer:
    """
    Воспроизведение WAV-файлов в отдельном потоке.
    """

    def __init__(self, sounds_dir: str = "sounds"):
        """
        :param sounds_dir: Папка со звуковыми файлами
        """
        self.sounds_dir = Path(sounds_dir)
        # Создаём папку если её нет
        if not self.sounds_dir.exists():
            self.sounds_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Папка sounds создана: {self.sounds_dir}")

    def play(self, sound_name: str) -> bool:
        """
        Воспроизводит WAV-файл в отдельном потоке.

        :param sound_name: Имя файла или полный путь
        :return: True если воспроизведение запущено
        """
        if not sound_name or not isinstance(sound_name, str):
            return False

        thread = threading.Thread(target=self._play_sound, args=(sound_name,), daemon=True)
        thread.start()
        return True

    def _play_sound(self, sound_name: str) -> None:
        """
        Внутренний метод воспроизведения.

        :param sound_name: Имя файла
        """
        try:
            sound_path: Optional[Path] = None

            # Проверяем путь относительно папки sounds
            if not Path(sound_name).is_absolute():
                sound_path = self.sounds_dir / sound_name

            # Если файл не найден, пробуем как абсолютный путь
            if not sound_path or not sound_path.exists():
                sound_path = Path(sound_name)
                if not sound_path.exists():
                    logger.warning(f"🔊 Звуковой файл не найден: {sound_name}")
                    return

            # Windows: используем winsound
            if os.name == 'nt':
                try:
                    import winsound
                    # SND_ASYNC для асинхронного воспроизведения
                    winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                    logger.debug(f"🔊 Воспроизведён звук: {sound_name}")
                    return
                except ImportError:
                    pass

                # Fallback через PowerShell
                try:
                    subprocess.run(
                        ["powershell", "-c",
                         f"(New-Object Media.SoundPlayer '{sound_path}').PlaySync()"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                    logger.debug(f"🔊 Воспроизведён звук (PowerShell): {sound_name}")
                    return
                except Exception as e:
                    logger.warning(f"PowerShell audio failed: {e}")

            logger.warning(f"❌ Не удалось воспроизвести звук: {sound_name} (нет плеера)")

        except Exception as e:
            logger.warning(f"Ошибка воспроизведения звука '{sound_name}': {e}")
