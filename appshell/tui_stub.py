"""Deterministic APPSHELL-0 TUI stub surface."""

from __future__ import annotations

from typing import Iterable, Mapping


def build_tui_stub(product_id: str, command_rows: Iterable[Mapping[str, object]], panel_rows: Iterable[Mapping[str, object]]) -> dict:
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "mode": "tui",
        "status": "stub",
        "commands": [dict(row) for row in list(command_rows or [])],
        "panels": [dict(row) for row in list(panel_rows or [])],
        "message": "APPSHELL-0 TUI stub is active.",
    }


__all__ = ["build_tui_stub"]
