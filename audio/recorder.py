# audio/recorder.py
"""
Модуль записи аудио и получения текста.
"""
import json
import time
from typing import Optional, List

import pyaudio

from utils.logger import get_logger
from audio.stream import AUDIO_BUFFER_SIZE, MAX_OVERFLOW_COUNT
from audio.vad import EnergyVAD

logger = get_logger(__name__)


class AudioRecorder:
    """
    Запись аудио с микрофона и распознавание.
    """

    def __init__(
        self,
        overflow_limit: int = MAX_OVERFLOW_COUNT,
        vad: Optional[EnergyVAD] = None,
        use_vad: bool = True
    ):
        """
        :param overflow_limit: Лимит ошибок переполнения буфера
        :param vad: Детектор речи (VAD) или None
        :param use_vad: Использовать ли VAD
        """
        self.overflow_limit = overflow_limit
        self.vad = vad or EnergyVAD()
        self.use_vad = use_vad

    def listen_once(
        self,
        recognizer,
        stream: pyaudio.Stream,
        timeout_sec: int,
        shutdown_flag=None,
        max_duration: int = 15
    ) -> Optional[str]:
        """
        Слушает микрофон в течение таймаута.

        :param recognizer: KaldiRecognizer
        :param stream: Аудиопоток PyAudio
        :param timeout_sec: Таймаут прослушивания (секунды)
        :param shutdown_flag: Флаг завершения работы (опционально)
        :param max_duration: Максимальная длительность записи (секунды)
        :return: Распознанный текст или None
        """
        start_time = time.time()
        overflow_count = 0
        
        # Ограничиваем общую длительность записи
        max_end_time = start_time + max_duration

        while time.time() - start_time < timeout_sec and time.time() < max_end_time:
            # Проверка флага завершения
            if shutdown_flag is not None and shutdown_flag():
                return None

            try:
                data = stream.read(AUDIO_BUFFER_SIZE, exception_on_overflow=False)

                # === VAD: пропускаем тишину ===
                if self.use_vad and not self.vad.is_speech(data):
                    continue

                # Передаём только речь в Vosk
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()

                    if text:
                        logger.debug(f"Распознано: {text}")
                        recognizer.Reset()
                        return text

            except OSError as e:
                overflow_count += 1
                logger.warning(f"Переполнение аудио-буфера ({overflow_count}): {e}")

                if overflow_count > self.overflow_limit:
                    logger.error("Слишком много переполнений. Перезапуск потока...")
                    return None

                time.sleep(0.01)
                continue

            except Exception as e:
                logger.exception(f"Ошибка при чтении аудио: {e}")
                return None

        # Попытка получить промежуточный результат
        try:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()

            if partial_text:
                logger.debug(f"Частичный результат: {partial_text}")
                recognizer.Reset()
                return partial_text

        except Exception as e:
            logger.warning(f"Ошибка при получении partial результата: {e}")

        recognizer.Reset()
        return None

    def listen_multiple(
        self,
        recognizer,
        stream: pyaudio.Stream,
        count: int,
        timeout_per_listen: int,
        shutdown_flag=None,
        max_duration: int = 15
    ) -> List[str]:
        """
        Слушает микрофон несколько раз.

        :param recognizer: KaldiRecognizer
        :param stream: Аудиопоток
        :param count: Количество попыток
        :param timeout_per_listen: Таймаут одной попытки
        :param shutdown_flag: Флаг завершения
        :param max_duration: Максимальная длительность записи
        :return: Список распознанных текстов
        """
        results: List[str] = []

        for _ in range(count):
            text = self.listen_once(
                recognizer,
                stream,
                timeout_per_listen,
                shutdown_flag,
                max_duration=max_duration
            )
            if text:
                results.append(text)
            if shutdown_flag is not None and shutdown_flag():
                break

        return results
