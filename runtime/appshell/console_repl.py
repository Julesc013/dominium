"""Deterministic REPL stub for AppShell console sessions."""

from __future__ import annotations

from typing import Iterable, Mapping


def build_console_session_stub(product_id: str, command_rows: Iterable[Mapping[str, object]]) -> dict:
    commands = [
        str(dict(row).get("command_path", "")).strip()
        for row in list(command_rows or [])
        if str(dict(row).get("command_path", "")).strip() and not str(dict(row).get("command_path", "")).strip().endswith(".*")
    ]
    commands = sorted(dict.fromkeys(commands))
    examples = []
    for command_text in ("help", "compat-status", "packs verify --root .", "diag capture", "console sessions"):
        command_path = " ".join(str(command_text).split()[:2]).strip()
        exact_path = " ".join(str(command_text).split()).strip()
        if exact_path in commands or command_path in commands:
            examples.append(command_text)
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "console_available": True,
        "prompt": "dominium> ",
        "welcome_message": "Type `help` to list commands. Use `compat-status` to inspect the current product surface.",
        "common_actions": [
            {"label": "Help", "command_text": "help"},
            {"label": "Compatibility", "command_text": "compat-status"},
            {"label": "Packs", "command_text": "packs verify --root ."},
            {"label": "Diagnostics", "command_text": "diag capture"},
        ],
        "examples": examples,
        "commands": commands,
    }


def run_scripted_console_session(product_id: str, commands: Iterable[str] | None = None) -> dict:
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "executed_commands": [str(item).strip() for item in list(commands or []) if str(item).strip()],
        "summary": "deterministic scripted console session complete",
    }


__all__ = ["build_console_session_stub", "run_scripted_console_session"]
