# actions/base.py
"""
Базовый класс для исполнителей действий.
"""
from typing import Dict, Any, Optional

from sound import SoundPlayer
from utils.logger import get_logger

logger = get_logger(__name__)


class ActionExecutor:
    """
    Базовый класс для всех исполнителей действий.
    """

    def __init__(self, sound_player: Optional[SoundPlayer] = None):
        """
        :param sound_player: Плеер для звуковой обратной связи
        """
        self.sound_player = sound_player or SoundPlayer()

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет действие. Должен быть переопределён в наследниках.

        :param action_def: Определение действия из конфига
        :return: True если успешно
        """
        raise NotImplementedError("Метод execute должен быть переопределён")

    def play_sound(self, sound_name: str) -> bool:
        """
        Воспроизводит звук.

        :param sound_name: Имя звукового файла
        :return: True если воспроизведение запущено
        """
        if sound_name:
            return self.sound_player.play(sound_name)
        return False

    def get_action_type(self) -> str:
        """
        Возвращает тип действия. Должен быть переопределён.

        :return: Строка типа действия
        """
        raise NotImplementedError("Метод get_action_type должен быть переопределён")
