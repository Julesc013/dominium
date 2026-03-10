"""Compatibility wrapper for the shared AppShell log engine."""

from src.appshell.logging import append_jsonl, build_log_event

__all__ = ["append_jsonl", "build_log_event"]
