"""Shared AppShell structured logging surfaces."""

from .log_engine import (
    LogEngine,
    append_jsonl,
    build_default_log_file_path,
    build_log_event,
    clear_current_log_engine,
    create_log_engine,
    get_current_log_engine,
    log_emit,
    set_current_log_engine,
)

__all__ = [
    "LogEngine",
    "append_jsonl",
    "build_default_log_file_path",
    "build_log_event",
    "clear_current_log_engine",
    "create_log_engine",
    "get_current_log_engine",
    "log_emit",
    "set_current_log_engine",
]
