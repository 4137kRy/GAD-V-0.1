# utils/list_mics.py
"""
Утилита для вывода списка доступных аудиоустройств.
Запустите этот скрипт, чтобы узнать ID вашего микрофона.
"""
import pyaudio


def list_microphones():
    """Выводит список всех доступных микрофонов."""
    p = pyaudio.PyAudio()
    
    print("=" * 60)
    print("📋 Доступные аудиоустройства")
    print("=" * 60)
    
    input_devices = []
    
    for i in range(p.get_device_count()):
        try:
            device_info = p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels', 0) > 0:
                input_devices.append({
                    'id': device_info['index'],
                    'name': device_info['name'],
                    'input_channels': device_info.get('maxInputChannels', 0),
                    'default_sample_rate': device_info.get('defaultSampleRate', 0)
                })
        except Exception:
            continue
    
    if input_devices:
        print("\n🎤 Входные устройства (микрофоны):")
        print("-" * 60)
        for dev in input_devices:
            print(f"   ID: {dev['id']}")
            print(f"   Название: {dev['name']}")
            print(f"   Каналы: {dev['input_channels']}")
            print(f"   Частота: {dev['default_sample_rate']} Гц")
            print("-" * 60)
    else:
        print("\n🎤 Входные устройства не найдены")
    
    print("\n💡 Чтобы использовать конкретный микрофон:")
    print("   1. Скопируйте ID нужного устройства")
    print("   2. Откройте config/settings.json")
    print("   3. Установите \"microphone_id\": <ваш_ID>")
    print("   4. Сохраните файл и перезапустите помощника")
    print("=" * 60)
    
    p.terminate()
    return input_devices


if __name__ == "__main__":
    list_microphones()
