# audio/device.py
"""
Модуль работы с аудиоустройствами.
"""
import time
from typing import Optional

import pyaudio

from utils.logger import get_logger
from audio.stream import AUDIO_BUFFER_SIZE, SAMPLE_RATE, find_best_input_device, get_device_info_by_id

logger = get_logger(__name__)


def wait_for_audio_device(
    max_attempts: int = 10,
    delay: int = 2,
    device_id: Optional[int] = None
) -> bool:
    """
    Ждёт готовности аудиоустройства.

    :param max_attempts: Максимальное количество попыток
    :param delay: Задержка между попытками (секунды)
    :param device_id: ID микрофона (None = автовыбор)
    :return: True если устройство готово
    """
    p = pyaudio.PyAudio()

    # Используем заданный device_id или находим лучший
    if device_id is not None:
        device_info = get_device_info_by_id(p, device_id)
        if device_info is None:
            logger.warning(f"⚠️ Устройство ID {device_id} недоступно, пробуем автовыбор...")
            device_index = find_best_input_device(p)
        else:
            device_index = device_id
    else:
        device_index = find_best_input_device(p)

    for attempt in range(max_attempts):
        try:
            stream_kwargs = {
                'format': pyaudio.paInt16,
                'channels': 1,
                'rate': SAMPLE_RATE,
                'input': True,
                'frames_per_buffer': AUDIO_BUFFER_SIZE
            }

            if device_index is not None:
                stream_kwargs['input_device_index'] = device_index

            test_stream = p.open(**stream_kwargs)
            test_stream.close()
            p.terminate()
            logger.info(f"✅ Аудиоустройство готово (попытка {attempt + 1})")
            return True
        except Exception as e:
            logger.warning(f"⏳ Аудиоустройство не готово (попытка {attempt + 1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
    p.terminate()
    logger.error("❌ Аудиоустройство не стало доступным")
    return False
