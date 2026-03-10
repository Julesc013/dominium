"""Deterministic REPL stub for AppShell console sessions."""

from __future__ import annotations

from typing import Iterable, Mapping


def build_console_session_stub(product_id: str, command_rows: Iterable[Mapping[str, object]]) -> dict:
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "console_available": True,
        "commands": [
            str(dict(row).get("command_path", "")).strip()
            for row in list(command_rows or [])
            if str(dict(row).get("command_path", "")).strip() and not str(dict(row).get("command_path", "")).strip().endswith(".*")
        ],
    }


def run_scripted_console_session(product_id: str, commands: Iterable[str] | None = None) -> dict:
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "executed_commands": [str(item).strip() for item in list(commands or []) if str(item).strip()],
    }


__all__ = ["build_console_session_stub", "run_scripted_console_session"]
