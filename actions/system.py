# actions/system.py
"""
Исполнитель системных команд.
"""
import os
import subprocess
from typing import Dict, Any

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemExecutor(ActionExecutor):
    """
    Выполнение системных команд: shutdown, sleep, logout.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет системную команду.

        :param action_def: Определение действия
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")

        success = False

        if action_type == "systemShutdown":
            if os.name == 'nt':
                subprocess.run(["shutdown", "/s", "/t", "5"], check=False)
            success = True
            logger.info("🔌 Система будет завершена через 5 секунд")

        elif action_type == "systemSleep":
            if os.name == 'nt':
                subprocess.run(
                    ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                    check=False
                )
            success = True
            logger.info("💤 Система переведена в сон")

        elif action_type == "systemLogout":
            if os.name == 'nt':
                subprocess.run(["shutdown", "/l"], check=False)
            success = True
            logger.info("🚪 Выполнен выход из системы")

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def get_action_type(self) -> str:
        return "system"
