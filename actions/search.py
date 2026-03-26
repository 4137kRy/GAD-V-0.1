# actions/search.py
"""
Исполнитель команды поиска в Google.
"""
import webbrowser
from urllib.parse import quote
from typing import Dict, Any, Optional

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchExecutor(ActionExecutor):
    """
    Поиск в Google: webSearch.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет поиск в Google.

        :param action_def: Определение действия с полем 'query'
        :return: True если успешно
        """
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")
        query = action_def.get("query", "")

        success = False

        if action_type == "webSearch":
            success = self._search_google(query)

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _search_google(self, query: Optional[str]) -> bool:
        """
        Открывает поиск в Google с заданным запросом.

        :param query: Поисковый запрос
        :return: True если успешно
        """
        if not query or not isinstance(query, str):
            logger.error("Поисковый запрос не указан")
            return False

        query = query.strip()
        if not query:
            logger.error("Поисковый запрос пустой")
            return False

        # Кодируем запрос для URL
        encoded_query = quote(query.encode('utf-8'))
        url = f"https://www.google.com/search?q={encoded_query}"

        try:
            webbrowser.open(url)
            logger.info(f"🔍 Поиск в Google: '{query}' → {url}")
            return True
        except Exception as e:
            logger.error(f"Ошибка открытия поиска: {e}")
            return False

    def get_action_type(self) -> str:
        return "search"
