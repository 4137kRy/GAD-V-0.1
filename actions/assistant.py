# actions/assistant.py
"""
Исполнитель команд управления ассистентом.
"""
import time
from typing import Dict, Any

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class AssistantExecutor(ActionExecutor):
    """
    Управление ассистентом: deactivate, stop.
    """

    def __init__(self, *args, **kwargs):
        """Инициализирует исполнителя."""
        super().__init__(*args, **kwargs)
        self._should_stop = False
        self._should_deactivate = False

    @property
    def should_stop(self) -> bool:
        """Флаг остановки ассистента."""
        return self._should_stop

    @property
    def should_deactivate(self) -> bool:
        """Флаг деактивации ассистента."""
        return self._should_deactivate

    def reset_flags(self) -> None:
        """Сбрасывает флаги."""
        self._should_stop = False
        self._should_deactivate = False

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет команду управления ассистентом.

        :param action_def: Определение действия
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")

        success = False

        if action_type == "assistantDeactivate":
            self._should_deactivate = True
            success = True
            logger.info("🔄 Помощник переведён в режим ожидания по команде")

        elif action_type == "assistantStop":
            logger.info("🛑 Остановка помощника по команде...")
            if sound_out:
                self.play_sound(sound_out)
                time.sleep(0.5)
            self._should_stop = True
            success = True

        # Для других типов (не assistant) — возвращаем False
        if action_type not in ("assistantDeactivate", "assistantStop"):
            logger.warning(f"Неподдерживаемый тип действия: {action_type}")
            return False

        # Звук уже воспроизведён для assistantStop
        if action_type == "assistantDeactivate" and sound_out:
            self.play_sound(sound_out)

        return success

    def get_action_type(self) -> str:
        return "assistant"
