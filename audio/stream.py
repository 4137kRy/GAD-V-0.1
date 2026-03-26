# audio/stream.py
"""
Модуль управления аудиопотоком.
"""
import time
from typing import Tuple, Optional

import pyaudio

from utils.logger import get_logger

logger = get_logger(__name__)

# Константы
SAMPLE_RATE = 16000
AUDIO_BUFFER_SIZE = 2048  # Уменьшен для более быстрой реакции (было 4000)
MAX_RETRIES = 5
RETRY_DELAY = 1
MAX_OVERFLOW_COUNT = 10


def find_best_input_device(pa: pyaudio.PyAudio) -> Optional[int]:
    """
    Находит лучшее доступное устройство для записи.
    Приоритет: DirectSound > WASAPI > MME > WDM-KS

    :param pa: Экземпляр PyAudio
    :return: ID устройства или None
    """
    host_api_order = [pyaudio.paDirectSound, pyaudio.paWASAPI, pyaudio.paMME, pyaudio.paWDMKS]

    for host_api in host_api_order:
        try:
            api_info = pa.get_host_api_info_by_type(host_api)

            for i in range(api_info['deviceCount']):
                try:
                    device_info = pa.get_device_info_by_host_api_device_index(host_api, i)
                    if device_info.get('maxInputChannels', 0) > 0:
                        logger.info(f"🎤 Найдено устройство: {device_info['name']} (API: {api_info['name']})")
                        return device_info['index']
                except Exception:
                    continue
        except Exception:
            continue

    # Если ничего не найдено, пробуем устройство по умолчанию
    try:
        default_device = pa.get_default_input_device_info()
        if default_device.get('maxInputChannels', 0) > 0:
            logger.info(f"🎤 Используется устройство по умолчанию: {default_device['name']}")
            return default_device['index']
    except Exception:
        pass

    return None


def get_device_info_by_id(pa: pyaudio.PyAudio, device_id: int) -> Optional[dict]:
    """
    Получает информацию об устройстве по его ID.

    :param pa: Экземпляр PyAudio
    :param device_id: ID устройства
    :return: Информация об устройстве или None
    """
    try:
        device_info = pa.get_device_info_by_index(device_id)
        if device_info.get('maxInputChannels', 0) > 0:
            logger.info(f"🎤 Используется устройство ID {device_id}: {device_info['name']}")
            return device_info
        else:
            logger.warning(f"⚠️ Устройство ID {device_id} не имеет входных каналов")
            return None
    except Exception as e:
        logger.error(f"❌ Устройство ID {device_id} недоступно: {e}")
        return None


def list_audio_devices() -> list:
    """
    Выводит список всех доступных аудиоустройств.

    :return: Список устройств с информацией
    """
    p = pyaudio.PyAudio()
    devices = []
    
    try:
        for i in range(p.get_device_count()):
            try:
                device_info = p.get_device_info_by_index(i)
                devices.append({
                    'id': device_info['index'],
                    'name': device_info['name'],
                    'input_channels': device_info.get('maxInputChannels', 0),
                    'output_channels': device_info.get('maxOutputChannels', 0),
                    'default_sample_rate': device_info.get('defaultSampleRate', 0)
                })
            except Exception:
                continue
    finally:
        p.terminate()
    
    return devices


def print_audio_devices() -> None:
    """
    Выводит в лог список всех доступных аудиоустройств.
    """
    devices = list_audio_devices()
    logger.info("=" * 60)
    logger.info("📋 Доступные аудиоустройства:")
    logger.info("=" * 60)
    
    input_devices = [d for d in devices if d['input_channels'] > 0]
    output_devices = [d for d in devices if d['output_channels'] > 0]
    
    if input_devices:
        logger.info("🎤 Входные устройства (микрофоны):")
        for dev in input_devices:
            logger.info(f"   ID: {dev['id']}, Название: {dev['name']}, Каналы: {dev['input_channels']}")
    else:
        logger.info("🎤 Входные устройства не найдены")
    
    if output_devices:
        logger.info("🔊 Выходные устройства (динамики):")
        for dev in output_devices:
            logger.info(f"   ID: {dev['id']}, Название: {dev['name']}, Каналы: {dev['output_channels']}")
    else:
        logger.info("🔊 Выходные устройства не найдены")
    
    logger.info("=" * 60)


class AudioStream:
    """
    Управление аудиопотоком PyAudio.
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        buffer_size: int = AUDIO_BUFFER_SIZE,
        device_index: Optional[int] = None
    ):
        """
        :param sample_rate: Частота дискретизации
        :param buffer_size: Размер буфера
        :param device_index: ID аудиоустройства (None = автовыбор)
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.device_index = device_index
        self._pa: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None

    @property
    def pa(self) -> Optional[pyaudio.PyAudio]:
        """Экземпляр PyAudio."""
        return self._pa

    @property
    def stream(self) -> Optional[pyaudio.Stream]:
        """Аудиопоток."""
        return self._stream

    def open(self) -> Tuple[pyaudio.PyAudio, pyaudio.Stream]:
        """
        Открывает аудиопоток с повторными попытками.

        :return: (pyaudio_instance, stream)
        :raises Exception: Если не удалось открыть поток
        """
        self._pa = pyaudio.PyAudio()

        # Автовыбор устройства если не задано
        if self.device_index is None:
            self.device_index = find_best_input_device(self._pa)

        for attempt in range(MAX_RETRIES):
            try:
                stream_kwargs = {
                    'format': pyaudio.paInt16,
                    'channels': 1,
                    'rate': self.sample_rate,
                    'input': True,
                    'frames_per_buffer': self.buffer_size
                }
                
                # Если устройство найдено, используем его
                if self.device_index is not None:
                    stream_kwargs['input_device_index'] = self.device_index
                    logger.info(f"🎤 Используем устройство ID: {self.device_index}")
                
                self._stream = self._pa.open(**stream_kwargs)
                logger.info(f"✅ Аудиопоток открыт (попытка {attempt + 1})")
                return self._pa, self._stream
            except Exception as e:
                logger.warning(f"⚠️ Ошибка открытия потока (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    self.close()
                    raise

        raise Exception("Не удалось открыть аудиопоток")

    def start(self) -> None:
        """Запускает аудиопоток."""
        if self._stream:
            self._stream.start_stream()
            logger.info("✅ Аудио-поток запущен")

    def stop(self) -> None:
        """Останавливает аудиопоток."""
        if self._stream:
            self._stream.stop_stream()
            logger.debug("🛑 Аудио-поток остановлен")

    def close(self) -> None:
        """Закрывает аудиопоток и PyAudio."""
        if self._stream:
            try:
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        if self._pa:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None

        logger.debug("🔌 Аудио-ресурсы освобождены")

    def __enter__(self) -> 'AudioStream':
        """Контекстный менеджер: вход."""
        self.open()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер: выход."""
        self.stop()
        self.close()
