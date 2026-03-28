# main.py
import re
import sys
from pathlib import Path

# ==============================================================================
# 1. Инициализация логирования
# ==============================================================================
from utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

# ==============================================================================
# 2. Импорт основных модулей
# ==============================================================================
from core import (
    SessionManager,
    setup_signal_handlers,
    get_shutdown_flag,
    reset_shutdown_flag
)
from audio import (
    wait_for_audio_device,
    AudioStream,
    VoskRecognizer,
    AudioRecorder,
    EnergyVAD,
    DEFAULT_MODEL_PATH,
    DEFAULT_THRESHOLD,
    print_audio_devices
)
from state import AssistantState, StateMachine, ConfirmationState
from text import normalize_text, build_allowed_words, correct_text_tokens
from parser import find_command
from actions import ActionDispatcher
from config import load_config, normalize_config, load_settings, get_microphone_id

# ==============================================================================
# 3. Константы
# ==============================================================================
CONFIG_PATH = "config/commands.json"
VAD_THRESHOLD = DEFAULT_THRESHOLD  # Порог VAD (настраивается)

# Таймауты прослушивания (секунды)
LISTEN_TIMEOUT_WAITING = 10  # В режиме ожидания (после активационной фразы)
LISTEN_TIMEOUT_ACTIVE = 8    # В активном режиме
LISTEN_TIMEOUT_CONFIRM = 6   # При ожидании подтверждения
LISTEN_MAX_DURATION = 15     # Максимальная длительность записи (ограничение)


# ==============================================================================
# 4. Основной класс помощника
# ==============================================================================
class VoiceAssistant:
    """
    Голосовой помощник GAD.
    """

    def __init__(self, config_path: str = CONFIG_PATH):
        """
        :param config_path: Путь к конфигурации
        """
        self.config_path = config_path
        self.config = None
        self.settings = None
        self.microphone_id = None

        # Компоненты
        self.session_manager: SessionManager = None
        self.state_machine: StateMachine = None
        self.confirmation_state: ConfirmationState = None
        self.audio_stream: AudioStream = None
        self.vosk: VoskRecognizer = None
        self.recorder: AudioRecorder = None
        self.action_dispatcher: ActionDispatcher = None
        self.vad: EnergyVAD = None

        # Данные
        self.activation_phrases = set()
        self.confirm_words = set()
        self.cancel_words = set()
        self.allowed_words = set()

    def load_config(self) -> bool:
        """
        Загружает и нормализует конфигурацию.

        :return: True если успешно
        """
        try:
            logger.info("Загрузка конфигурации...")
            raw_config = load_config(self.config_path)
            self.config = normalize_config(raw_config)

            # Извлекаем данные
            self.activation_phrases = set(self.config.get("activation_phrases", []))

            # Фразы подтверждения
            confirmation_phrases = self.config.get("confirmation_phrases", {})
            for phrase in confirmation_phrases.get("confirm", []):
                if isinstance(phrase, str):
                    self.confirm_words.update(normalize_text(phrase).split())
            for phrase in confirmation_phrases.get("cancel", []):
                if isinstance(phrase, str):
                    self.cancel_words.update(normalize_text(phrase).split())

            # Если фразы не заданы — используем значения по умолчанию
            if not self.confirm_words:
                self.confirm_words = {"уверен", "да", "подтверждаю"}
                logger.warning("[WARN] Фразы подтверждения не заданы, используются значения по умолчанию")

            if not self.cancel_words:
                self.cancel_words = {"отмена", "нет", "не надо"}
                logger.warning("[WARN] Фразы отмены не заданы, используются значения по умолчанию")

            # Словарь допустимых слов
            self.allowed_words = build_allowed_words(self.config)

            logger.info(f"[OK] Загружено {len(self.activation_phrases)} активационных фраз")
            logger.info(f"[OK] Загружено {len(self.allowed_words)} допустимых слов")
            logger.info(f"[OK] Фразы подтверждения: {self.confirm_words}")
            logger.info(f"[OK] Фразы отмены: {self.cancel_words}")

            return True

        except Exception as e:
            logger.critical(f"Ошибка загрузки конфигурации: {e}")
            return False

    def init_audio(self) -> bool:
        """
        Инициализирует аудио-подсистему.

        :return: True если успешно
        """
        # Загружаем настройки и получаем ID микрофона
        self.settings = load_settings()
        self.microphone_id = get_microphone_id(self.settings)
        
        # Выводим список доступных устройств
        print_audio_devices()
        
        if self.microphone_id is not None:
            logger.info(f"🎯 Используем микрофон ID: {self.microphone_id}")
        else:
            logger.info("🎯 Автовыбор микрофона")
        
        logger.info("🔍 Проверка доступности аудиоустройства...")

        if not wait_for_audio_device(device_id=self.microphone_id):
            logger.critical("Не удалось получить доступ к микрофону")
            logger.info("💡 Попробуйте перезапустить программу через 30 секунд")
            return False

        try:
            self.audio_stream = AudioStream(device_index=self.microphone_id)
            self.audio_stream.open()
            self.audio_stream.start()

            self.vosk = VoskRecognizer(DEFAULT_MODEL_PATH)
            if not self.vosk.load():
                return False

            # Инициализация VAD
            self.vad = EnergyVAD(threshold=VAD_THRESHOLD)
            logger.info(f"✅ VAD инициализирован (порог: {VAD_THRESHOLD})")

            # Создаём рекордер с VAD
            self.recorder = AudioRecorder(vad=self.vad, use_vad=True)

            logger.info("✅ Аудио-подсистема инициализирована")
            return True

        except Exception as e:
            logger.critical(f"Ошибка инициализации аудио: {e}")
            return False

    def init_components(self) -> None:
        """
        Инициализирует компоненты.
        """
        self.session_manager = SessionManager()
        self.state_machine = StateMachine()
        self.confirmation_state = ConfirmationState()
        self.action_dispatcher = ActionDispatcher()

        logger.info("✅ Компоненты инициализированы")

    def check_confirmation_response(self, normalized_text: str) -> tuple:
        """
        Проверяет ответ подтверждения.

        :param normalized_text: Нормализованный текст
        :return: (is_confirm, is_cancel)
        """
        tokens = normalized_text.split()
        is_confirm = any(word in self.confirm_words for word in tokens)
        is_cancel = any(word in self.cancel_words for word in tokens)
        return (is_confirm, is_cancel)

    def handle_confirmation(self, normalized_text: str) -> bool:
        """
        Обрабатывает ответ подтверждения.

        :param normalized_text: Нормализованный текст
        :return: True если команда выполнена или отменена
        """
        is_confirm, is_cancel = self.check_confirmation_response(normalized_text)

        if is_confirm:
            command = self.confirmation_state.get_command()
            if command:
                logger.info(f"✅ Подтверждение получено. Выполняю: {command['identifier']}/{command['verb']}")

                search_query = command.get('search_query')
                success = self.action_dispatcher.execute(
                    command['identifier'],
                    command['verb'],
                    self.config,
                    search_query=search_query
                )

                # Проверяем флаги остановки/деактивации
                if self.action_dispatcher.assistant_executor.should_stop:
                    logger.info("🛑 Выход из основного цикла по команде...")
                    return True  # Сигнал остановки

                if self.action_dispatcher.assistant_executor.should_deactivate:
                    self.state_machine.deactivate()
                else:
                    self.session_manager.update_command_time()

                self.confirmation_state.reset()
                self.action_dispatcher.assistant_executor.reset_flags()

                logger.info(f"{'✅ Успешно' if success else '❌ Ошибка'}: {command['identifier']}/{command['verb']}")
                return True

        elif is_cancel:
            logger.info("❌ Команда отменена пользователем")
            self.confirmation_state.reset()
            self.session_manager.update_command_time()
            return True

        else:
            # Непонятный ответ
            attempts = self.confirmation_state.increment_attempt()
            logger.warning(f"⚠️ Непонятный ответ (попытка {attempts}/{self.confirmation_state.max_attempts})")

            if self.confirmation_state.is_max_attempts_reached():
                logger.info("❌ Превышено количество попыток подтверждения. Команда отменена")
                self.confirmation_state.reset()
                self.session_manager.update_command_time()
            else:
                logger.info("🔄 Пожалуйста, скажите 'уверен' для подтверждения или 'отмена' для отмены")

            return False

    def handle_command(self, normalized_text: str) -> bool:
        """
        Обрабатывает команду.

        :param normalized_text: Нормализованный текст
        :return: True если команда распознана
        """
        command = find_command(normalized_text, self.config)

        if not command:
            logger.debug("Команда не распознана")
            return False

        identifier_key = command['identifier']
        verb_key = command['verb']
        requires_confirmation = command['requires_confirmation']

        logger.info(f"🎯 Команда распознана: {identifier_key}/{verb_key}")

        # Специальная обработка команды "найди" - извлекаем поисковый запрос
        search_query = None
        if identifier_key == "find" or identifier_key == "_any":
            # Извлекаем текст после слов "найди", "поиск", "погугли", "загугли"
            search_query = self._extract_search_query(normalized_text)
            logger.info(f"🔍 Поисковый запрос: '{search_query}'")

        # Проверяем требование подтверждения
        if requires_confirmation:
            logger.info("⚠️ Команда требует подтверждения")
            logger.info("📢 Пожалуйста, скажите 'уверен' для подтверждения или 'отмена' для отмены")

            self.confirmation_state.start({
                'identifier': identifier_key,
                'verb': verb_key,
                'search_query': search_query
            })
            self.session_manager.update_command_time()
            return True

        # Выполняем действие
        success = self.action_dispatcher.execute(
            identifier_key,
            verb_key,
            self.config,
            search_query=search_query
        )

        # Проверяем флаги
        if self.action_dispatcher.assistant_executor.should_stop:
            logger.info("🛑 Выход из основного цикла по команде...")
            return True  # Сигнал остановки

        if self.action_dispatcher.assistant_executor.should_deactivate:
            self.state_machine.deactivate()
        else:
            self.session_manager.update_command_time()

        self.action_dispatcher.assistant_executor.reset_flags()
        logger.info(f"{'✅ Успешно' if success else '❌ Ошибка'}: {identifier_key}/{verb_key}")
        return True

    def handle_activation(self, normalized_text: str, cmd_text: str) -> None:
        """
        Обрабатывает активационную фразу.

        :param normalized_text: Полный текст
        :param cmd_text: Текст команды после активации
        """
        logger.info("✅ Активационная фраза распознана")

        if not cmd_text:
            self.state_machine.activate()
            self.session_manager.update_command_time()
            logger.info("🎯 Ожидаю команду в активном режиме...")
        else:
            self.state_machine.activate()
            logger.info(f"📝 Команда в активации: '{cmd_text}'")
            self.handle_command(cmd_text)

    def remove_activation_phrases(self, text: str) -> str:
        """
        Удаляет слова активации из текста.

        :param text: Исходный текст
        :return: Текст без активации
        """
        cmd_text = text
        for phrase in self.activation_phrases:
            cmd_text = cmd_text.replace(phrase, "  ")
        cmd_text = re.sub(r'\s+', ' ', cmd_text).strip()
        return cmd_text

    def _extract_search_query(self, normalized_text: str) -> str:
        """
        Извлекает поисковый запрос из текста после слов "найди", "поиск", "погугли", "загугли".

        :param normalized_text: Нормализованный текст
        :return: Поисковый запрос
        """
        search_words = ["найди", "поиск", "погугли", "загугли", "гугл", "google"]
        result = normalized_text

        for word in search_words:
            if word in result:
                # Удаляем слово поиска и всё до него
                idx = result.find(word)
                result = result[idx + len(word):].strip()
                break

        return result

    def run(self) -> int:
        """
        Основной цикл работы.

        :return: Код выхода
        """
        logger.info("=" * 60)
        logger.info("Запуск голосового помощника...")
        logger.info("=" * 60)

        # Загрузка конфигурации
        if not self.load_config():
            return 1

        # Инициализация компонентов
        self.init_components()

        # Инициализация аудио
        if not self.init_audio():
            return 1

        # Установка обработчиков сигналов
        setup_signal_handlers()

        logger.info("💤 Режим ожидания. Говорите активационную фразу...")
        logger.info("📢 Пример: 'помощник', 'слушай меня', 'ок помощник'")
        logger.info("🔧 Калибровка VAD: скажите 'калибруй шум' в активном режиме")

        try:
            while not get_shutdown_flag():
                # Проверка таймаута бездействия
                if self.state_machine.is_active and self.session_manager.check_active_timeout():
                    self.state_machine.deactivate()
                    self.confirmation_state.reset()
                    logger.info("⏰ Активный режим завершён по таймауту. Возврат в ожидание.")

                # Определяем таймаут прослушивания в зависимости от режима
                is_confirmation = self.confirmation_state.pending
                is_waiting = self.state_machine.is_waiting
                timeout = self.session_manager.get_listen_timeout(
                    is_confirmation=is_confirmation,
                    is_waiting=is_waiting
                )

                # Максимальная длительность записи
                max_duration = self.session_manager.get_max_listen_duration()

                # Получаем текст из микрофона
                recognizer = self.vosk.recognizer
                stream = self.audio_stream.stream

                raw_text = self.recorder.listen_once(
                    recognizer,
                    stream,
                    timeout,
                    get_shutdown_flag,
                    max_duration=max_duration
                )

                if not raw_text:
                    continue

                # Нормализация и логирование
                norm_text = normalize_text(raw_text)
                logger.info(f"🎤 Распознано: '{raw_text}' → '{norm_text}'")

                # =====================================================================
                # Обработка подтверждения (приоритет)
                # =====================================================================
                if self.confirmation_state.pending:
                    if self.handle_confirmation(norm_text):
                        if self.action_dispatcher.assistant_executor.should_stop:
                            break
                        if self.action_dispatcher.assistant_executor.should_restart:
                            logger.info("🔁 Запуск перезапуска...")
                            self._cleanup_audio()
                            if not self.load_config():
                                return 1
                            if not self.init_audio():
                                return 1
                            self.action_dispatcher.assistant_executor.reset_restart_flag()
                    continue

                # =====================================================================
                # Обработка активации
                # =====================================================================
                if self.state_machine.is_waiting:
                    has_activation = any(
                        phrase in norm_text
                        for phrase in self.activation_phrases
                    )

                    if not has_activation:
                        logger.debug("Активационная фраза не найдена")
                        continue

                    cmd_text = self.remove_activation_phrases(norm_text)
                    self.handle_activation(norm_text, cmd_text)

                    if self.action_dispatcher.assistant_executor.should_stop:
                        break
                    if self.action_dispatcher.assistant_executor.should_restart:
                        logger.info("🔁 Запуск перезапуска...")
                        self._cleanup_audio()
                        if not self.load_config():
                            return 1
                        if not self.init_audio():
                            return 1
                        self.action_dispatcher.assistant_executor.reset_restart_flag()

                    continue

                # =====================================================================
                # Обработка команды в активном режиме
                # =====================================================================
                if self.state_machine.is_active:
                    # Специальная команда: калибровка VAD
                    if "калибруй шум" in norm_text or "калибровка vad" in norm_text:
                        logger.info("🔧 Запуск калибровки VAD...")
                        self.vad.auto_calibrate_threshold(stream, duration_sec=3.0)
                        self.session_manager.update_command_time()
                        continue

                    # Исправление опечаток
                    tokens = norm_text.split()
                    corrected_tokens = correct_text_tokens(tokens, self.allowed_words, max_distance=2)
                    corrected_text = " ".join(corrected_tokens)

                    if corrected_text != norm_text:
                        logger.info(f"🔧 Исправлено: '{norm_text}' → '{corrected_text}'")

                    if self.handle_command(corrected_text):
                        if self.action_dispatcher.assistant_executor.should_stop:
                            break
                        # Проверяем флаг перезапуска после выполнения команды
                        if self.action_dispatcher.assistant_executor.should_restart:
                            logger.info("🔁 Запуск перезапуска...")
                            self._cleanup_audio()
                            if not self.load_config():
                                return 1
                            if not self.init_audio():
                                return 1
                            self.action_dispatcher.assistant_executor.reset_restart_flag()

        except KeyboardInterrupt:
            logger.info("Получен сигнал прерывания")
        except Exception as e:
            logger.exception(f"Критическая ошибка: {e}")
        finally:
            # Очистка ресурсов
            logger.info("Очистка ресурсов...")

            # Логирование статистики VAD
            if self.vad:
                stats = self.vad.get_stats()
                logger.info(f"📊 Статистика VAD: {stats}")

            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()

        logger.info("=" * 60)
        logger.info("Голосовой помощник остановлен")
        logger.info("=" * 60)
        return 0

    def _cleanup_audio(self) -> None:
        """
        Очищает аудио-ресурсы для перезапуска.
        """
        logger.info("🔇 Остановка аудио...")
        if self.vad:
            stats = self.vad.get_stats()
            logger.info(f"📊 Статистика VAD: {stats}")
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
        logger.info("✅ Аудио остановлено")


# ==============================================================================
# 5. Точка входа
# ==============================================================================
def main() -> int:
    """
    Точка входа в приложение.

    :return: Код выхода
    """
    assistant = VoiceAssistant()
    return assistant.run()


if __name__ == "__main__":
    sys.exit(main())
