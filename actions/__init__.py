# actions/__init__.py
"""
Модуль исполнения действий голосового помощника.
"""
from typing import Dict, Any, Optional

from sound import SoundPlayer
from actions.base import ActionExecutor
from actions.system import SystemExecutor
from actions.window import WindowExecutor
from actions.media import MediaExecutor
from actions.volume import VolumeExecutor
from actions.application import ApplicationExecutor
from actions.navigation import NavigationExecutor
from actions.assistant import AssistantExecutor
from actions.search import SearchExecutor

from utils.logger import get_logger

logger = get_logger(__name__)


class ActionDispatcher:
    """
    Диспетчер действий: маршрутизирует по типам.
    """

    def __init__(self, sound_player: Optional[SoundPlayer] = None):
        """
        :param sound_player: Плеер для звуковой обратной связи
        """
        self.sound_player = sound_player or SoundPlayer()

        # Инициализируем исполнители
        self._executors: Dict[str, ActionExecutor] = {
            "system": SystemExecutor(self.sound_player),
            "window": WindowExecutor(self.sound_player),
            "media": MediaExecutor(self.sound_player),
            "volume": VolumeExecutor(self.sound_player),
            "application": ApplicationExecutor(self.sound_player),
            "navigation": NavigationExecutor(self.sound_player),
            "assistant": AssistantExecutor(self.sound_player),
            "search": SearchExecutor(self.sound_player),
        }

        # Маппинг типов действий к исполнителям
        self._action_type_map = {
            # System
            "systemShutdown": "system",
            "systemSleep": "system",
            "systemLogout": "system",
            # Window
            "windowMaximize": "window",
            "windowMinimize": "window",
            "windowClose": "window",
            "windowSwitchNext": "window",
            "windowSwitchPrev": "window",
            "focusWindow": "window",
            # Media
            "mediaPlay": "media",
            "mediaPause": "media",
            "mediaNext": "media",
            "mediaPrev": "media",
            # Volume
            "volumeUp": "volume",
            "volumeDown": "volume",
            "volumeMuteToggle": "volume",
            # Application
            "exeStart": "application",
            "killProcess": "application",
            # Navigation
            "urlOpen": "navigation",
            "fileOpen": "navigation",
            # Search
            "webSearch": "search",
            # Assistant
            "assistantDeactivate": "assistant",
            "assistantStop": "assistant",
        }

    def execute(
        self,
        identifier_key: str,
        verb_key: str,
        config: Dict[str, Any],
        search_query: Optional[str] = None
    ) -> bool:
        """
        Выполняет действие по ключам.

        :param identifier_key: Ключ идентификатора
        :param verb_key: Ключ глагола
        :param config: Конфигурация
        :param search_query: Поисковый запрос (для команды "найди")
        :return: True если успешно
        """
        try:
            actions = config.get("actions", {})
            if identifier_key not in actions:
                logger.error(f"Идентификатор '{identifier_key}' не найден в actions")
                return False

            if verb_key not in actions[identifier_key]:
                logger.error(f"Глагол '{verb_key}' не найден для '{identifier_key}'")
                return False

            action_def = actions[identifier_key][verb_key].copy()
        except (KeyError, TypeError) as e:
            logger.error(f"Комбинация ({identifier_key}, {verb_key}) не найдена: {e}")
            return False

        # Для поиска подменяем query из параметра
        if search_query and action_def.get("type") == "webSearch":
            action_def["query"] = search_query

        action_type = action_def.get("type")
        if not action_type:
            logger.error("Поле 'type' отсутствует в определении действия")
            return False

        logger.info(f"⚙️ Выполняю: {action_type} ({identifier_key} / {verb_key})")

        # Находим исполнителя
        executor_key = self._action_type_map.get(action_type)
        if not executor_key:
            logger.error(f"❌ Неизвестный тип действия: '{action_type}'")
            return False

        executor = self._executors.get(executor_key)
        if not executor:
            logger.error(f"Исполнитель не найден: {executor_key}")
            return False

        return executor.execute(action_def)

    def get_executor(self, action_type: str) -> Optional[ActionExecutor]:
        """
        Возвращает исполнителя по типу действия.

        :param action_type: Тип действия
        :return: Исполнитель или None
        """
        executor_key = self._action_type_map.get(action_type)
        if executor_key:
            return self._executors.get(executor_key)
        return None

    @property
    def assistant_executor(self) -> AssistantExecutor:
        """Возвращает исполнителя команд ассистента."""
        return self._executors["assistant"]


# Создаём глобальный экземпляр для обратной совместимости
_dispatcher: Optional[ActionDispatcher] = None


def get_dispatcher() -> ActionDispatcher:
    """
    Возвращает глобальный диспетчер действий.

    :return: ActionDispatcher
    """
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = ActionDispatcher()
    return _dispatcher


def execute_action(identifier_key: str, verb_key: str, config: Dict[str, Any]) -> bool:
    """
    Выполняет действие (для обратной совместимости).

    :param identifier_key: Ключ идентификатора
    :param verb_key: Ключ глагола
    :param config: Конфигурация
    :return: True если успешно
    """
    return get_dispatcher().execute(identifier_key, verb_key, config)
