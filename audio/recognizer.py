# audio/recognizer.py
"""
Модуль распознавания речи Vosk.
"""
import json
from typing import Optional
from pathlib import Path

from vosk import Model, KaldiRecognizer

from utils.logger import get_logger
from audio.stream import SAMPLE_RATE

logger = get_logger(__name__)

# Путь к модели по умолчанию
DEFAULT_MODEL_PATH = str(Path("models") / "vosk-model-small-ru-0.22")


class VoskRecognizer:
    """
    Обёртка вокруг KaldiRecognizer для распознавания речи.
    """

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        """
        :param model_path: Путь к модели Vosk
        """
        self.model_path = Path(model_path)
        self._model: Optional[Model] = None
        self._recognizer: Optional[KaldiRecognizer] = None

    @property
    def model(self) -> Optional[Model]:
        """Модель Vosk."""
        return self._model

    @property
    def recognizer(self) -> Optional[KaldiRecognizer]:
        """Распознаватель Kaldi."""
        return self._recognizer

    def load(self) -> bool:
        """
        Загружает модель и инициализирует распознаватель.

        :return: True если загрузка успешна
        """
        if not self.model_path.exists():
            logger.critical(f"Модель не найдена: {self.model_path.absolute()}")
            logger.info("📥 Скачайте русскую модель с https://alphacephei.com/vosk/models")
            logger.info("📁 Распакуйте в папку 'models'")
            return False

        logger.info(f"Загрузка модели Vosk из: {self.model_path}")
        self._model = Model(str(self.model_path))
        self._recognizer = KaldiRecognizer(self._model, SAMPLE_RATE)
        logger.info("✅ Модель загружена")
        return True

    def reset(self) -> None:
        """Сбрасывает состояние распознавателя."""
        if self._recognizer:
            self._recognizer.Reset()
            logger.debug("🔄 Распознаватель сброшен")
