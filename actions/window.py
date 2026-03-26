# actions/window.py
"""
Исполнитель команд управления окнами.
"""
from typing import Dict, Any, Optional

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)

# Проверка зависимостей
keyboard = None
gw = None

try:
    import keyboard
    logger.debug("✅ Модуль 'keyboard' доступен для управления окнами")
except ImportError:
    logger.warning("⚠️ Модуль 'keyboard' не установлен. Горячие клавиши недоступны.")

try:
    import pygetwindow as gw
    logger.debug("✅ Модуль 'pygetwindow' доступен для управления окнами")
except ImportError:
    logger.warning("⚠️ Модуль 'pygetwindow' не установлен. Управление окнами недоступно.")


class WindowExecutor(ActionExecutor):
    """
    Управление окнами: maximize, minimize, close, switch.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет команду управления окном.

        :param action_def: Определение действия
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")
        title_contains = action_def.get("title_contains")

        success = False

        if action_type == "windowMaximize":
            success = self._maximize_window()

        elif action_type == "windowMinimize":
            success = self._minimize_window()

        elif action_type == "windowClose":
            success = self._close_window()

        elif action_type == "windowSwitchNext":
            success = self._switch_next()

        elif action_type == "windowSwitchPrev":
            success = self._switch_prev()

        elif action_type == "focusWindow":
            success = self._focus_window(title_contains)

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _maximize_window(self) -> bool:
        """Разворачивает активное окно."""
        if gw:
            active = gw.getActiveWindow()
            if active:
                active.maximize()
                logger.debug("✅ Окно развёрнуто")
                return True
            logger.warning("Нет активного окна для развёртывания")
        else:
            logger.warning("Модуль 'pygetwindow' недоступен")
        return False

    def _minimize_window(self) -> bool:
        """Сворачивает активное окно."""
        if gw:
            active = gw.getActiveWindow()
            if active:
                active.minimize()
                logger.debug("✅ Окно свёрнуто")
                return True
            logger.warning("Нет активного окна для сворачивания")
        else:
            logger.warning("Модуль 'pygetwindow' недоступен")
        return False

    def _close_window(self) -> bool:
        """Закрывает активное окно (Alt+F4)."""
        if keyboard:
            keyboard.send("alt+f4")
            logger.debug("✅ Окно закрыто (Alt+F4)")
            return True
        logger.warning("Модуль 'keyboard' недоступен")
        return False

    def _switch_next(self) -> bool:
        """Переключает на следующее окно (Alt+Tab)."""
        if keyboard:
            keyboard.send("alt+tab")
            logger.debug("✅ Переключено на следующее окно")
            return True
        return False

    def _switch_prev(self) -> bool:
        """Переключает на предыдущее окно (Alt+Shift+Tab)."""
        if keyboard:
            keyboard.send("alt+shift+tab")
            logger.debug("✅ Переключено на предыдущее окно")
            return True
        return False

    def _focus_window(self, title_contains: Optional[str]) -> bool:
        """Активирует окно по заголовку."""
        if not title_contains:
            logger.error("Заголовок окна не указан")
            return False

        if not gw:
            logger.warning("Модуль 'pygetwindow' недоступен")
            return False

        try:
            windows = gw.getWindowsWithTitle(title_contains)
            if windows:
                windows[0].activate()
                logger.info(f"✅ Активировано окно: {title_contains}")
                return True
            logger.warning(f"Окно с '{title_contains}' не найдено")
            return False
        except Exception as e:
            logger.error(f"Ошибка при активации окна: {e}")
            return False

    def get_action_type(self) -> str:
        return "window"
