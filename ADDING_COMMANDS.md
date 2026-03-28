# 📝 Как добавить свою команду в GAD

Это руководство объясняет **как работает система команд** и показывает **пошагово** как добавлять:
1. Новые команды с существующими типами действий
2. Совершенно новые типы действий (свои type)

---

## 📋 Оглавление

1. [Как работает система команд](#как-работает-система-команд)
2. [Добавление команды с существующим типом действия](#добавление-команды-с-существующим-типом-действия)
3. [Добавление своего типа действия](#добавление-своего-типа-действия)
4. [Примеры для копирования](#примеры-для-копирования)

---

## 🔍 Как работает система команд

### Общая схема

```
Вы говорите: «открой дискорд»
        │
        ▼
┌───────────────────────────────────────────────────┐
│  1. Распознавание речи (Vosk)                     │
│     → текст: "открой дискорд"                     │
└───────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────┐
│  2. Нормализация текста                           │
│     → "открой дискорд" (нижний регистр)           │
└───────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────┐
│  3. Парсинг: поиск идентификатора и глагола       │
│     • Ищем в identifiers: "дискорд" → "discord"   │
│     • Ищем в verbs: "открой" → "open"             │
└───────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────┐
│  4. Поиск действия в actions                      │
│     actions["discord"]["open"]                    │
│     → { type: "exeStart", path: "...", ... }      │
└───────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────┐
│  5. Выполнение по типу действия                   │
│     type: "exeStart" → ApplicationExecutor        │
│     → запускает процесс по пути path              │
└───────────────────────────────────────────────────┘
```

### Три ключевых раздела конфига

Все команды настраиваются в **одном файле** — `config/commands.json`.

В нём есть **три главных раздела**:

#### 1️⃣ `identifiers` — **ЧТО управляем** (объект)

Это существительные — объекты, которыми управляем:

```json
"identifiers": {
  "browser": ["браузер", "интернет"],
  "calculator": ["калькулятор", "счёт"],
  "discord": ["дискорд", "дс"]
}
```

- Ключ слева (`"browser"`, `"discord"`) — **внутреннее имя** (латиницей)
- Список справа — **слова которые вы произносите** (по-русски)

Когда вы говорите «дискорд», система понимает: это идентификатор `discord`.

---

#### 2️⃣ `verbs` — **ЧТО делаем** (действие)

Это глаголы — действия над объектами:

```json
"verbs": {
  "open": ["открой", "запусти", "включи"],
  "close": ["закрой", "выключи", "останови"]
}
```

- Ключ слева (`"open"`, `"close"`) — **внутреннее имя** глагола (латиницей)
- Список справа — **слова которые вы произносите** (по-русски)

Когда вы говорите «открой», система понимает: это глагол `open`.

---

#### 3️⃣ `actions` — **КАК выполняем** (правило)

Это связь идентификатора + глагола с конкретным действием:

```json
"actions": {
  "discord": {
    "open": { "type": "exeStart", "path": "C:\\Discord\\Discord.exe" },
    "close": { "type": "killProcess", "process": "Discord.exe" }
  }
}
```

Структура:
```
actions[идентификатор][глагол] = правило выполнения
```

- `discord` + `open` → запустить процесс (`exeStart`)
- `discord` + `close` → убить процесс (`killProcess`)

**Поле `type`** — это **тип действия**. Он определяет, какой исполнитель (ActionExecutor) будет вызван.

---

### Как это работает вместе

| Вы говорите | identifiers | verbs | actions |
|-------------|-------------|-------|---------|
| «открой дискорд» | `дискорд` → `discord` | `открой` → `open` | `actions["discord"]["open"]` |
| «закрой браузер» | `браузер` → `browser` | `закрой` → `close` | `actions["browser"]["close"]` |

**Логика поиска:**
1. Распознали текст → «открой дискорд»
2. Нашли в тексте `дискорд` → идентификатор `discord`
3. Нашли в тексте `открой` → глагол `open`
4. Ищем `actions["discord"]["open"]` → находим правило
5. Смотрим `type` правила → вызываем нужный исполнитель

---

## ➕ Добавление команды с существующим типом действия

Это **самый частый случай** — вы хотите добавить новую команду, используя уже готовые типы действий.

### Какие типы действий уже есть

| Type | Что делает | Какие поля нужны |
|------|------------|------------------|
| `exeStart` | Запускает программу | `path` (путь к .exe) |
| `killProcess` | Закрывает программу | `process` (имя процесса) |
| `urlOpen` | Открывает сайт в браузере | `url` (адрес сайта) |
| `fileOpen` | Открывает файл | `file` (путь к файлу) |
| `mediaPlay` | Включает музыку/видео | `file` (путь к медиа) |
| `mediaPause` | Пауза воспроизведения | — |
| `mediaNext` | Следующий трек | — |
| `mediaPrev` | Предыдущий трек | — |
| `volumeUp` | Громче | — |
| `volumeDown` | Тише | — |
| `volumeMuteToggle` | Вкл/выкл звук | — |
| `windowMaximize` | Развернуть окно | — |
| `windowMinimize` | Свернуть окно | — |
| `windowClose` | Закрыть окно | — |
| `windowSwitchNext` | Следующее окно (Alt+Tab) | — |
| `windowSwitchPrev` | Предыдущее окно | — |
| `focusWindow` | Активировать окно по заголовку | `title_contains` |
| `systemShutdown` | Выключить ПК | — |
| `systemSleep` | Сон | — |
| `systemLogout` | Выйти из системы | — |
| `assistantDeactivate` | Режим ожидания | — |
| `assistantStop` | Остановить помощника | — |
| `webSearch` | Поиск в Google | `query` (запрос) |

---

### Пошаговая инструкция

#### Шаг 1: Откройте конфиг

Файл: **`config/commands.json`**

---

#### Шаг 2: Добавьте идентификатор

Найдите раздел `"identifiers"` и добавьте новую строку:

```json
"identifiers": {
  "browser": ["браузер", "интернет"],
  "calculator": ["калькулятор", "счёт"],
  "discord": ["дискорд", "дс", "голосовой чат"]
}
```

**Правила:**
- Ключ слева (`"discord"`) — только **латиницей**, lowercase, без пробелов
- Слова справа — **по-русски**, в кавычках, через запятую
- Это те слова, которые вы будете **произносить вслух**

---

#### Шаг 3: Добавьте действие

Найдите раздел `"actions"` и добавьте правило для вашего идентификатора:

```json
"actions": {
  "browser": {
    "open": { "type": "exeStart", "path": "..." }
  },
  "discord": {
    "open": { "type": "exeStart", "path": "C:\\Users\\User\\AppData\\Local\\Discord\\Discord.exe", "sound_out": "SWO.wav" },
    "close": { "type": "killProcess", "process": "Discord.exe", "sound_out": "SWO.wav" }
  }
}
```

**Структура:**
```
"ваш_идентификатор": {
  "глагол_1": { "type": "тип_действия", ...поля... },
  "глагол_2": { "type": "тип_действия", ...поля... }
}
```

**Важно:**
- Пути Windows экранируйте: `C:\\Path\\File.exe` (два обратных слеша)
- `sound_out` — имя WAV-файла для звука (необязательно)

---

#### Шаг 4: Сохраните и перезапустите

1. **Сохраните** `config/commands.json`
2. **Перезапустите** помощника: закройте и запустите `start.bat` снова
3. **Скажите команду**: «открой дискорд»

---

### Полный пример: добавляем Telegram

**Хотим:** чтобы помощник открывал и закрывал Telegram по командам «открой телеграм», «закрой тг».

**Шаг 1 — идентификатор:**

```json
"identifiers": {
  "telegram": ["телеграм", "тг", "телегу"]
}
```

**Шаг 2 — действие:**

```json
"actions": {
  "telegram": {
    "open": { "type": "exeStart", "path": "C:\\Users\\User\\AppData\\Roaming\\Telegram\\Telegram.exe", "sound_out": "SWO.wav" },
    "close": { "type": "killProcess", "process": "Telegram.exe", "sound_out": "SWO.wav" }
  }
}
```

**Готово!** Теперь работают команды:
- «открой телеграм» → запускает Telegram
- «закрой тг» → закрывает Telegram

---

## 🛠 Добавление своего типа действия

Используйте этот раздел, если вам **не хватает существующих типов** (`exeStart`, `killProcess`, etc.) и вы хотите создать **совершенно новый тип действия**.

Например:
- Отправка сообщения в Telegram
- Отправка email
- Управление умным домом
- Запись в файл лога

---

### Общая схема

```
config/commands.json          actions/
┌─────────────────────┐      ┌───────────────────────┐
│ "actions": {        │      │ my_action.py          │
│   "telegram_msg": { │      │ ┌───────────────────┐ │
│     "send": {       │─────▶│ │ MyActionExecutor  │ │
│       "type":       │      │ │ - execute()       │ │
│       "telegramSend"│      │ │ - get_action_type │ │
│     }               │      │ └───────────────────┘ │
│   }                 │      └───────────────────────┘
└─────────────────────┘                 │
                                        ▼
                              actions/__init__.py
                              ┌───────────────────────┐
                              │ Регистрация:          │
                              │ "telegramSend" →      │
                              │ MyActionExecutor      │
                              └───────────────────────┘
```

---

### Пошаговая инструкция

#### Шаг 1: Создайте файл исполнителя

Создайте новый файл в папке `actions/`:

**Файл:** `actions/my_action.py`

```python
# actions/my_action.py
"""
Описание: что делает этот исполнитель.
"""
from typing import Dict, Any

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class MyActionExecutor(ActionExecutor):
    """
    Краткое описание исполнителя.
    """

    def execute(self, action_def: Dict[str, Any]) -> bool:
        """
        Выполняет действие.

        :param action_def: Определение действия из конфига
        :return: True если успешно
        """
        # Получаем тип действия
        action_type = action_def.get("type")

        # Получаем звук (если указан)
        sound_out = action_def.get("sound_out")

        # Получаем ваши параметры из конфига
        param1 = action_def.get("param1", "")
        param2 = action_def.get("param2", "")

        success = False

        # Выполняем нужное действие
        if action_type == "myActionType":
            success = self._do_something(param1, param2)

        # Воспроизводим звук если указан и всё успешно
        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _do_something(self, param1: str, param2: str) -> bool:
        """
        Ваша логика действия.

        :param param1: Параметр 1
        :param param2: Параметр 2
        :return: True если успешно
        """
        try:
            # 🔹 Здесь ваш код
            # Например: отправка сообщения, запись в файл, etc.
            logger.info(f"Выполняю действие с {param1} и {param2}")
            return True
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return False

    def get_action_type(self) -> str:
        """
        Возвращает имя типа действия.
        """
        return "my_action"
```

---

#### Шаг 2: Зарегистрируйте исполнителя

Откройте **`actions/__init__.py`** и добавьте:

**1. Импорт в начале файла:**

```python
from actions.my_action import MyActionExecutor
```

**2. Добавьте исполнителя в `_executors`:**

```python
self._executors: Dict[str, ActionExecutor] = {
    # Существующие исполнители
    "system": SystemExecutor(self.sound_player),
    "window": WindowExecutor(self.sound_player),
    "media": MediaExecutor(self.sound_player),
    # ...
    "my_action": MyActionExecutor(self.sound_player),
}
```

**3. Добавьте тип действия в `_action_type_map`:**

```python
self._action_type_map = {
    # Существующие типы
    "systemShutdown": "system",
    "exeStart": "application",
    # ...
    "myActionType": "my_action",
}
```

**Важно:**
- Ключ в `_action_type_map` (`"myActionType"`) — это то, что вы указываете в конфиге как `type`
- Значение (`"my_action"`) — это ключ исполнителя в `_executors`

---

#### Шаг 3: Используйте в конфиге

Теперь используйте ваш тип в **`config/commands.json`**:

```json
"identifiers": {
  "telegram_msg": ["сообщение", "отправь сообщение"]
},
"verbs": {
  "send": ["отправь", "пошли", "напиши"]
},
"actions": {
  "telegram_msg": {
    "send": { "type": "myActionType", "param1": "значение1", "param2": "значение2", "sound_out": "SWO.wav" }
  }
}
```

---

#### Шаг 4: Перезапустите помощника

```bash
start.bat
```

Теперь команда работает с вашим типом действия!

---

## 📚 Примеры для копирования

### Пример 1: Отправка email (свой тип)

**Файл:** `actions/email_action.py`

```python
# actions/email_action.py
"""
Отправка email через SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class EmailActionExecutor(ActionExecutor):
    """Отправка email."""

    def execute(self, action_def: Dict[str, Any]) -> bool:
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")

        to_addr = action_def.get("to", "")
        subject = action_def.get("subject", "")
        body = action_def.get("body", "")

        success = False

        if action_type == "emailSend":
            success = self._send_email(to_addr, subject, body)

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _send_email(self, to_addr: str, subject: str, body: str) -> bool:
        if not to_addr or not subject:
            logger.error("Пустой адрес или тема")
            return False

        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = "gad@localhost"
            msg['To'] = to_addr

            # Пример отправки (раскомментируйте и настройте):
            # with smtplib.SMTP('smtp.example.com', 587) as server:
            #     server.starttls()
            #     server.login('user@example.com', 'password')
            #     server.send_message(msg)

            logger.info(f"📧 Email: {to_addr} — {subject}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки email: {e}")
            return False

    def get_action_type(self) -> str:
        return "email_action"
```

**Регистрация в `actions/__init__.py`:**

```python
# Импорт
from actions.email_action import EmailActionExecutor

# В __init__:
self._executors = {
    # ...
    "email_action": EmailActionExecutor(self.sound_player),
}

self._action_type_map = {
    # ...
    "emailSend": "email_action",
}
```

**Конфиг:**

```json
"identifiers": {
  "email": ["почта", "email", "письмо"]
},
"verbs": {
  "send": ["отправь", "пошли"]
},
"actions": {
  "email": {
    "send": { "type": "emailSend", "to": "user@example.com", "subject": "Привет от GAD", "body": "Тестовое письмо.", "sound_out": "SWO.wav" }
  }
}
```

---

### Пример 2: Запись в лог (свой тип)

**Файл:** `actions/log_action.py`

```python
# actions/log_action.py
"""
Запись сообщения в лог-файл.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from actions.base import ActionExecutor
from utils.logger import get_logger
from utils.paths import get_project_root

logger = get_logger(__name__)


class LogActionExecutor(ActionExecutor):
    """Запись в лог-файл."""

    def execute(self, action_def: Dict[str, Any]) -> bool:
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")
        message = action_def.get("message", "")

        success = False

        if action_type == "logWrite":
            success = self._write_log(message)

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _write_log(self, message: str) -> bool:
        try:
            log_path = get_project_root() / "logs" / "commands.log"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")

            logger.info(f"📝 Запись в лог: {message}")
            return True
        except Exception as e:
            logger.error(f"Ошибка записи в лог: {e}")
            return False

    def get_action_type(self) -> str:
        return "log_action"
```

**Регистрация в `actions/__init__.py`:**

```python
from actions.log_action import LogActionExecutor

self._executors = {
    # ...
    "log_action": LogActionExecutor(self.sound_player),
}

self._action_type_map = {
    # ...
    "logWrite": "log_action",
}
```

**Конфиг:**

```json
"identifiers": {
  "log_cmd": ["запиши в лог", "лог"]
},
"verbs": {
  "write": ["запиши", "напиши"]
},
"actions": {
  "log_cmd": {
    "write": { "type": "logWrite", "message": "Пользователь выполнил команду", "sound_out": "SWO.wav" }
  }
}
```

---

### Пример 3: Запуск скрипта (свой тип)

**Файл:** `actions/script_action.py`

```python
# actions/script_action.py
"""
Запуск внешнего скрипта или программы.
"""
import subprocess
from typing import Dict, Any, List

from actions.base import ActionExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class ScriptActionExecutor(ActionExecutor):
    """Запуск скрипта."""

    def execute(self, action_def: Dict[str, Any]) -> bool:
        action_type = action_def.get("type")
        sound_out = action_def.get("sound_out")
        script_path = action_def.get("script", "")
        args = action_def.get("args", [])

        success = False

        if action_type == "scriptRun":
            success = self._run_script(script_path, args)

        if success and sound_out:
            self.play_sound(sound_out)

        return success

    def _run_script(self, script_path: str, args: List[str]) -> bool:
        if not script_path:
            logger.error("Путь к скрипту не указан")
            return False

        try:
            cmd = [script_path] + args
            subprocess.Popen(cmd)
            logger.info(f"🚀 Запуск скрипта: {script_path} {' '.join(args)}")
            return True
        except Exception as e:
            logger.error(f"Ошибка запуска скрипта: {e}")
            return False

    def get_action_type(self) -> str:
        return "script_action"
```

**Регистрация в `actions/__init__.py`:**

```python
from actions.script_action import ScriptActionExecutor

self._executors = {
    # ...
    "script_action": ScriptActionExecutor(self.sound_player),
}

self._action_type_map = {
    # ...
    "scriptRun": "script_action",
}
```

**Конфиг:**

```json
"identifiers": {
  "script": ["скрипт"]
},
"verbs": {
  "open": ["запусти", "выполни", "открой"]
},
"actions": {
  "script": {
    "open": { "type": "scriptRun", "script": "C:\\scripts\\myscript.bat", "args": ["--arg1", "--arg2"], "sound_out": "SWO.wav" }
  }
}
```

---

## 🐛 Отладка

### Команда не работает

**1. Проверьте логи:**

Откройте `logs/assistant.log` и ищите:
- `Команда не распознана` — проблема в identifiers/verbs
- `Идентификатор не найден` — проверьте название в actions
- `Неизвестный тип действия` — проверьте регистрацию типа

**2. Проверьте конфиг:**

Убедитесь что:
- Идентификатор в `identifiers` совпадает с ключом в `actions`
- Глагол в `verbs` совпадает с ключом внутри `actions[identifier]`
- Поле `type` указано правильно

**3. Проверьте пути:**

Для `exeStart`, `fileOpen`:
```python
from pathlib import Path
print(Path("C:\\Path\\To\\File.exe").exists())  # Должно быть True
```

### Звук не работает

- Проверьте что файл есть в `sounds/`
- Имя в `sound_out` должно точно совпадать (регистр важен!)

### Свой тип не работает

- Проверьте что импорт в `actions/__init__.py` правильный
- Проверьте что `_action_type_map` содержит ваш тип
- Перезапустите помощника после изменений

---

## ✅ Проверка JSON на ошибки

Перед перезапуском помощника **обязательно проверьте** что `config/commands.json` — валидный JSON.

**Способ 1: Онлайн-валидатор**

1. Откройте [jsonlint.com](https://jsonlint.com/)
2. Вставьте содержимое `config/commands.json`
3. Нажмите **Validate JSON**

**Способ 2: Через Python**

Запустите в терминале:
```bash
python -m json.tool config/commands.json > nul
```

Если ошибок нет — команда завершится без вывода. Если есть ошибка — увидите сообщение с номером строки.

**Способ 3: Через PowerShell**

```powershell
Get-Content config\commands.json | ConvertFrom-Json
```

Если JSON невалиден — PowerShell покажет ошибку.

---

## 📋 Чек-лист

### Добавление команды с существующим типом

```
□ Добавлен идентификатор в `identifiers`
□ Добавлено действие в `actions`
□ Указан правильный `type`
□ Заполнены нужные поля (path, process, url...)
□ Пути экранированы: C:\\Path\\File.exe
□ Сохранён config/commands.json
□ JSON проверен на ошибки (валидатор)
□ Перезапущен помощник
□ Протестирована команда
```

### Добавление своего типа действия

```
□ Создан файл actions/my_action.py
□ Создан класс-наследник ActionExecutor
□ Реализован метод execute()
□ Реализован метод get_action_type()
□ Импорт добавлен в actions/__init__.py
□ Исполнитель добавлен в _executors
□ Тип добавлен в _action_type_map
□ Использован новый type в config/commands.json
□ JSON проверен на ошибки (валидатор)
□ Перезапущен помощник
□ Протестирована команда
```

---

> 💡 **Совет:** Старайтесь сохранить модульную структуру. Не пишите все команды в одном Python-файле — разделяйте их по разным файлам (`email_action.py`, `log_action.py`, `script_action.py`). Это улучшит читаемость и упростит отладку.

---

**GAD — Офлайн Голосовой Помощник**  
[GitHub](https://github.com/4137kRy/GAD) | [Лицензия MIT](../LICENSE)
