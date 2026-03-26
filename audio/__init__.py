# audio/__init__.py
"""
Аудио-подсистема голосового помощника.
"""
from .stream import (
    AudioStream,
    SAMPLE_RATE,
    AUDIO_BUFFER_SIZE,
    MAX_OVERFLOW_COUNT,
    find_best_input_device,
    get_device_info_by_id,
    list_audio_devices,
    print_audio_devices
)
from .device import wait_for_audio_device
from .recognizer import VoskRecognizer, DEFAULT_MODEL_PATH
from .recorder import AudioRecorder
from .vad import EnergyVAD, DEFAULT_THRESHOLD, MIN_SPEECH_FRAMES, SILENCE_FRAMES

__all__ = [
    "AudioStream",
    "SAMPLE_RATE",
    "AUDIO_BUFFER_SIZE",
    "MAX_OVERFLOW_COUNT",
    "find_best_input_device",
    "get_device_info_by_id",
    "list_audio_devices",
    "print_audio_devices",
    "wait_for_audio_device",
    "VoskRecognizer",
    "DEFAULT_MODEL_PATH",
    "AudioRecorder",
    "EnergyVAD",
    "DEFAULT_THRESHOLD",
    "MIN_SPEECH_FRAMES",
    "SILENCE_FRAMES",
]
