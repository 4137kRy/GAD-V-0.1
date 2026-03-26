# audio/vad.py
"""
VAD (Voice Activity Detection) — детектор речевой активности.
Отфильтровывает тишину и фоновый шум перед передачей в Vosk.
"""
import math
from typing import Optional

import pyaudio

from utils.logger import get_logger

logger = get_logger(__name__)

# Константы VAD
DEFAULT_THRESHOLD = 150  # Порог громкости (0-32767 для 16-bit)
MIN_SPEECH_FRAMES = 1    # Мин. количество подряд идущих "громких" фреймов для детектирования речи
SILENCE_FRAMES = 5       # Количество "тихих" фреймов после речи для окончания записи


class EnergyVAD:
    """
    Энергетический детектор речи.
    
    Вычисляет RMS (root mean square) громкости каждого фрейма
    и сравнивает с порогом.
    """

    def __init__(
        self,
        threshold: int = DEFAULT_THRESHOLD,
        min_speech_frames: int = MIN_SPEECH_FRAMES,
        silence_frames: int = SILENCE_FRAMES
    ):
        """
        :param threshold: Порог громкости (0-32767)
        :param min_speech_frames: Мин. количество "громких" фреймов для начала записи
        :param silence_frames: Количество "тихих" фреймов для окончания записи
        """
        self.threshold = threshold
        self.min_speech_frames = min_speech_frames
        self.silence_frames = silence_frames
        
        # Состояние
        self._consecutive_speech_frames = 0
        self._consecutive_silence_frames = 0
        self._is_speaking = False
        self._speech_started = False
        
        # Статистика
        self._total_frames = 0
        self._processed_frames = 0
        self._skipped_silence_frames = 0

    def reset(self) -> None:
        """Сбрасывает состояние детектора."""
        self._consecutive_speech_frames = 0
        self._consecutive_silence_frames = 0
        self._is_speaking = False
        self._speech_started = False
        logger.debug("🔇 VAD сброшен")

    @staticmethod
    def calculate_rms(data: bytes) -> float:
        """
        Вычисляет RMS (root mean square) громкости аудио-фрейма.
        
        :param data: Аудио-данные (16-bit PCM)
        :return: RMS громкость (0-32767)
        """
        count = len(data) // 2  # 16-bit = 2 байта на сэмпл
        if count == 0:
            return 0.0
        
        # Преобразуем байты в сэмплы
        rms = 0.0
        for i in range(count):
            sample = int.from_bytes(data[i*2:(i+1)*2], byteorder='little', signed=True)
            rms += sample * sample
        
        rms = math.sqrt(rms / count)
        return rms

    def is_speech(self, data: bytes) -> bool:
        """
        Проверяет, содержит ли фрейм речь.
        
        :param data: Аудио-фрейм
        :return: True если обнаружена речь
        """
        self._total_frames += 1
        rms = self.calculate_rms(data)
        
        # Проверяем порог
        if rms >= self.threshold:
            self._consecutive_speech_frames += 1
            self._consecutive_silence_frames = 0
            
            # Речь началась, если достаточно подряд идущих "громных" фреймов
            if not self._is_speaking and self._consecutive_speech_frames >= self.min_speech_frames:
                self._is_speaking = True
                self._speech_started = True
                logger.debug(f"🎤 Речь обнаружена (RMS: {rms:.1f})")
            
            # Продолжаем считать пока говорим
            if self._is_speaking:
                self._processed_frames += 1
                return True
        else:
            self._consecutive_speech_frames = 0
            self._consecutive_silence_frames += 1
            
            # Если говорим и достигли порога тишины — речь закончилась
            if self._is_speaking and self._consecutive_silence_frames >= self.silence_frames:
                logger.debug(f"🔇 Речь завершена (RMS: {rms:.1f}, обработано фреймов: {self._processed_frames})")
                self._is_speaking = False
                self._speech_started = False
                self._processed_frames = 0
                return False
            
            # Если ещё не начали говорить — пропускаем тишину
            if not self._is_speaking:
                self._skipped_silence_frames += 1
                return False
            
            # Всё ещё в режиме речи (недостаточно тишины)
            if self._is_speaking:
                self._processed_frames += 1
                return True
        
        return self._is_speaking

    @property
    def is_speaking(self) -> bool:
        """Текущее состояние: идёт речь или нет."""
        return self._is_speaking

    @property
    def speech_started(self) -> bool:
        """Была ли обнаружена речь с момента последнего сброса."""
        return self._speech_started

    def get_stats(self) -> dict:
        """
        Возвращает статистику работы VAD.
        
        :return: Статистика
        """
        total = max(self._total_frames, 1)
        return {
            "total_frames": self._total_frames,
            "processed_frames": self._processed_frames,
            "skipped_silence_frames": self._skipped_silence_frames,
            "silence_ratio": f"{self._skipped_silence_frames / total * 100:.1f}%",
            "cpu_saved": f"{self._skipped_silence_frames / total * 100:.1f}%",
        }

    def set_threshold(self, threshold: int) -> None:
        """
        Устанавливает новый порог громкости.
        
        :param threshold: Новый порог (0-32767)
        """
        self.threshold = threshold
        logger.info(f"🔧 Порог VAD установлен: {threshold}")

    def auto_calibrate_threshold(
        self,
        stream: pyaudio.Stream,
        duration_sec: float = 3.0,
        buffer_size: int = 4000,
        percentile: float = 0.7
    ) -> int:
        """
        Автоматически калибрует порог на основе фонового шума.
        
        :param stream: Аудиопоток
        :param duration_sec: Длительность калибровки (секунды)
        :param buffer_size: Размер буфера
        :param percentile: Процентиль для порога (0.0-1.0)
        :return: Установленный порог
        """
        logger.info(f"🔧 Калибровка VAD ({duration_sec} сек)...")
        
        rms_values = []
        frames_to_read = int(duration_sec * 16000 / buffer_size)
        
        for _ in range(frames_to_read):
            data = stream.read(buffer_size, exception_on_overflow=False)
            rms = self.calculate_rms(data)
            rms_values.append(rms)
        
        if not rms_values:
            logger.warning("⚠️ Не удалось получить данные для калибровки")
            return self.threshold
        
        # Сортируем и берём процентиль
        rms_values.sort()
        idx = int(len(rms_values) * percentile)
        noise_floor = rms_values[idx]
        
        # Порог = шум + 30% запаса
        new_threshold = int(noise_floor * 1.3)
        new_threshold = max(new_threshold, 50)   # Минимум 50
        new_threshold = min(new_threshold, 500)  # Максимум 500
        
        self.set_threshold(new_threshold)
        logger.info(f"✅ Порог установлен: {new_threshold} (шум: {noise_floor:.1f})")
        
        return new_threshold
