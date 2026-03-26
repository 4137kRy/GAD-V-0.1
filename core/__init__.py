# core/__init__.py
"""
Ядро голосового помощника.
"""
from .session import SessionManager, TIMEOUT_WAITING, ACTIVE_TIMEOUT, ACTIVE_LISTEN_TIMEOUT, CONFIRMATION_TIMEOUT
from .signals import (
    shutdown_requested,
    get_shutdown_flag,
    signal_handler,
    setup_signal_handlers,
    reset_shutdown_flag
)

__all__ = [
    "SessionManager",
    "TIMEOUT_WAITING",
    "ACTIVE_TIMEOUT",
    "ACTIVE_LISTEN_TIMEOUT",
    "CONFIRMATION_TIMEOUT",
    "shutdown_requested",
    "get_shutdown_flag",
    "signal_handler",
    "setup_signal_handlers",
    "reset_shutdown_flag",
]
