# actions/application.py
"""
Исполнитель команд запуска и закрытия приложений.
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from actions.base import ActionExecutor
from utils.paths import validate_path, MAX_PATH_LENGTH
from utils.logger import get_logger

logger = get_logger(__name__)


class ApplicationExecutor(ActionExecutor):
    """
    Запуск и закрытие приложений: exeStart, killProcess.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет команду приложения.

        :param action_def: Определение действия
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")

        success = False

        if action_type == "exeStart":
            path = action_def.get("path")
            success = self._start_executable(path)

        elif action_type == "killProcess":
            process_name = action_def.get("process")
            success = self._kill_process(process_name)

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _start_executable(self, path: Optional[str]) -> bool:
        """
        Запускает исполняемый файл.

        :param path: Путь к исполняемому файлу
        :return: True если успешно
        """
        if not path or not isinstance(path, str):
            logger.error("Путь к исполняемому файлу не указан")
            return False

        # Валидация пути
        is_valid, error_msg = validate_path(path, MAX_PATH_LENGTH)
        if not is_valid:
            logger.error(error_msg)
            return False

        try:
            # Для относительных путей ищем в PATH
            if not os.path.isabs(path):
                resolved_path = shutil.which(path)
                if not resolved_path:
                    logger.error(f"Исполняемый файл не найден в PATH: {path}")
                    return False
                path = resolved_path
                logger.debug(f"✅ Разрешён путь: {path}")

            # Проверка существования
            if not os.path.exists(path):
                logger.error(f"Файл не существует: {path}")
                return False

            # Запуск
            subprocess.Popen([path], shell=False)
            logger.info(f"✅ Запущено: {path}")
            return True

        except Exception as e:
            logger.error(f"Не удалось запустить '{path}': {e}")
            return False

    def _kill_process(self, process_name: Optional[str]) -> bool:
        """
        Завершает процесс.

        :param process_name: Имя процесса
        :return: True если успешно
        """
        if not process_name or not isinstance(process_name, str):
            logger.error("Имя процесса не указано")
            return False

        # Валидация имени
        import re
        if not re.match(r'^[\w.\- ]+$', process_name):
            logger.error(f"Подозрительное имя процесса: {process_name}")
            return False

        try:
            if os.name == 'nt':
                subprocess.run(
                    ["taskkill", "/IM", process_name, "/F"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            logger.info(f"✅ Процесс завершён: {process_name}")
            return True

        except subprocess.CalledProcessError:
            logger.warning(f"Процесс '{process_name}' не найден или не удалось завершить")
            return False
        except Exception as e:
            logger.error(f"Ошибка при завершении процесса: {e}")
            return False

    def get_action_type(self) -> str:
        return "application"
