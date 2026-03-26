# actions/volume.py
"""
Исполнитель команд громкости.
"""
import time
from typing import Dict, Any

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)

# Проверка зависимости
keyboard = None

try:
    import keyboard
    logger.debug("✅ Модуль 'keyboard' доступен для управления громкостью")
except ImportError:
    logger.warning("⚠️ Модуль 'keyboard' не установлен. Управление громкостью недоступно.")

# Константы
VOLUME_STEP_COUNT = 10
VOLUME_DELAY = 0.05


class VolumeExecutor(ActionExecutor):
    """
    Управление громкостью: up, down, mute.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет команду громкости.

        :param action_def: Определение действия
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")

        success = False

        if action_type == "volumeUp":
            success = self._volume_up()

        elif action_type == "volumeDown":
            success = self._volume_down()

        elif action_type == "volumeMuteToggle":
            success = self._mute_toggle()

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _volume_up(self) -> bool:
        """Увеличивает громкость."""
        if keyboard:
            for _ in range(VOLUME_STEP_COUNT):
                keyboard.send("volume up")
                time.sleep(VOLUME_DELAY)
            logger.debug(f"✅ Громкость увеличена ({VOLUME_STEP_COUNT} шагов)")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def _volume_down(self) -> bool:
        """Уменьшает громкость."""
        if keyboard:
            for _ in range(VOLUME_STEP_COUNT):
                keyboard.send("volume down")
                time.sleep(VOLUME_DELAY)
            logger.debug(f"✅ Громкость уменьшена ({VOLUME_STEP_COUNT} шагов)")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def _mute_toggle(self) -> bool:
        """Переключает mute."""
        if keyboard:
            keyboard.send("volume mute")
            logger.debug("✅ Звук переключён (mute)")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def get_action_type(self) -> str:
        return "volume"
