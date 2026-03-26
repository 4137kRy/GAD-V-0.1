# state/__init__.py
"""
Модуль управления состояниями.
"""
from .machine import AssistantState, StateMachine
from .confirmation import ConfirmationState

__all__ = [
    "AssistantState",
    "StateMachine",
    "ConfirmationState",
]
