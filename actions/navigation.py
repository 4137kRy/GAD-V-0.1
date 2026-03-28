# actions/navigation.py
"""
Исполнитель команд навигации: URL, файлы.
"""
import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

from actions.base import ActionExecutor
from utils.paths import validate_path
from utils.logger import get_logger

logger = get_logger(__name__)


class NavigationExecutor(ActionExecutor):
    """
    Навигация: urlOpen, fileOpen.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет команду навигации.

        :param action_def: Определение действия
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")

        success = False

        if action_type == "urlOpen":
            url = action_def.get("url")
            success = self._open_url(url)

        elif action_type == "fileOpen":
            file_path = action_def.get("file")
            success = self._open_file(file_path)

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _open_url(self, url: Optional[str]) -> bool:
        """
        Открывает URL в браузере.

        :param url: URL для открытия
        :return: True если успешно
        """
        if not url or not isinstance(url, str):
            logger.error("URL не указан")
            return False

        url = url.strip()
        if not url:
            logger.error("URL пустой")
            return False

        try:
            webbrowser.open(url)
            logger.info(f"🌐 Открыт URL: {url}")
            return True
        except Exception as e:
            logger.error(f"Ошибка открытия URL: {e}")
            return False

    def _open_file(self, file_path: Optional[str]) -> bool:
        """
        Открывает файл ассоциированным приложением.

        :param file_path: Путь к файлу
        :return: True если успешно
        """
        if not file_path or not isinstance(file_path, str):
            logger.error("Путь к файлу не указан")
            return False

        # Валидация
        is_valid, error_msg = validate_path(file_path)
        if not is_valid:
            logger.error(error_msg)
            return False

        path = Path(file_path)

        if not path.exists():
            logger.error(f"Файл не найден: {path.absolute()}")
            return False

        try:
            if os.name == 'nt':
                os.startfile(str(path))
            else:
                # Linux/macOS
                subprocess.run(["open" if os.name == "darwin" else "xdg-open", str(path)])

            logger.info(f"✅ Открыт файл: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Не удалось открыть файл '{file_path}': {e}")
            return False

    def get_action_type(self) -> str:
        return "navigation"
