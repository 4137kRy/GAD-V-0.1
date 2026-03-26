# utils/validators.py
"""
Модуль валидации данных для голосового помощника.
"""
from typing import Any, Dict, List, Tuple


def validate_config_structure(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Проверяет целостность и наличие обязательных секций в конфигурации.

    :param config: Словарь конфигурации
    :return: (is_valid, list_of_errors)
    """
    errors: List[str] = []

    # Проверка наличия обязательных разделов
    required_sections = ["activation_phrases", "identifiers", "verbs", "actions"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Отсутствует секция: {section}")

    actions = config.get("actions", {})
    identifiers = config.get("identifiers", {})
    verbs = config.get("verbs", {})

    # Проверка: у каждого идентификатора должны быть действия
    for ident_key in identifiers:
        if ident_key not in actions and ident_key != "system":
            errors.append(f"Идентификатор '{ident_key}' не имеет действий в actions")

    # Проверка: каждый глагол должен использоваться хотя бы в одном действии
    for verb_key in verbs:
        has_action = False
        for ident_key, ident_actions in actions.items():
            if verb_key in ident_actions:
                has_action = True
                break
        if not has_action:
            errors.append(f"Глагол '{verb_key}' не используется ни в одном действии")

    return (len(errors) == 0, errors)


def validate_action_def(action_def: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Проверяет корректность определения действия.

    :param action_def: Словарь действия
    :return: (is_valid, error_message)
    """
    if not isinstance(action_def, dict):
        return (False, "Действие должно быть словарём")

    if "type" not in action_def:
        return (False, "Действие не имеет поля 'type'")

    action_type = action_def.get("type")

    # Проверка обязательных полей для разных типов действий
    if action_type == "exeStart" and "path" not in action_def:
        return (False, "Действие exeStart требует поле 'path'")

    if action_type == "killProcess" and "process" not in action_def:
        return (False, "Действие killProcess требует поле 'process'")

    if action_type == "urlOpen" and "url" not in action_def:
        return (False, "Действие urlOpen требует поле 'url'")

    if action_type in ("fileOpen", "mediaPlay") and "file" not in action_def:
        return (False, f"Действие {action_type} требует поле 'file'")

    if action_type == "focusWindow" and "title_contains" not in action_def:
        return (False, "Действие focusWindow требует поле 'title_contains'")

    # Проверка поля requires_confirmation (опциональное)
    if "requires_confirmation" in action_def:
        conf_value = action_def["requires_confirmation"]
        if not isinstance(conf_value, bool):
            return (False, f"requires_confirmation должен быть boolean (получено {type(conf_value).__name__})")

    return (True, "")
