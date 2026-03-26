# actions/media.py
"""
Исполнитель медиа-команд.
"""
from typing import Dict, Any

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)

# Проверка зависимости
keyboard = None

try:
    import keyboard
    logger.debug("✅ Модуль 'keyboard' доступен для медиа-управления")
except ImportError:
    logger.warning("⚠️ Модуль 'keyboard' не установлен. Медиа-управление недоступно.")


class MediaExecutor(ActionExecutor):
    """
    Управление медиа: play, pause, next, prev.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет медиа-команду.

        :param action_def: Определение действия
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")

        success = False

        if action_type == "mediaPlay":
            success = self._play()

        elif action_type == "mediaPause":
            success = self._pause()

        elif action_type == "mediaNext":
            success = self._next()

        elif action_type == "mediaPrev":
            success = self._prev()

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _play(self) -> bool:
        """Запускает воспроизведение."""
        if keyboard:
            keyboard.send("play/pause media")
            logger.debug("✅ Воспроизведение запущено")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def _pause(self) -> bool:
        """Ставит на паузу."""
        if keyboard:
            keyboard.send("play/pause media")
            logger.debug("✅ Воспроизведение приостановлено")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def _next(self) -> bool:
        """Следующий трек."""
        if keyboard:
            keyboard.send("next media")
            logger.debug("✅ Следующий трек")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def _prev(self) -> bool:
        """Предыдущий трек."""
        if keyboard:
            keyboard.send("previous media")
            logger.debug("✅ Предыдущий трек")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def get_action_type(self) -> str:
        return "media"
