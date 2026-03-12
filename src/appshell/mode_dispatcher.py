"""Deterministic AppShell mode dispatch helpers."""

from __future__ import annotations

from typing import Iterable, Mapping

from .rendered_stub import build_rendered_stub
from .tui_stub import build_tui_stub
from .ui_mode_selector import default_mode_for_product as _default_mode_for_product
from .ui_mode_selector import supported_modes_for_product as _supported_modes_for_product


def supported_modes_for_product(product_id: str, repo_root: str = "") -> list[str]:
    return list(_supported_modes_for_product(str(product_id).strip(), repo_root=repo_root))


def default_mode_for_product(product_id: str, repo_root: str = "", context_kind: str = "tty") -> str:
    return _default_mode_for_product(str(product_id).strip(), repo_root=repo_root, context_kind=context_kind)


def normalize_mode(product_id: str, requested_mode: str, repo_root: str = "") -> str:
    token = str(requested_mode or "").strip().lower()
    if not token:
        return default_mode_for_product(product_id, repo_root=repo_root)
    if token in supported_modes_for_product(product_id, repo_root=repo_root):
        return token
    return token


def legacy_mode_args(product_id: str, mode_id: str) -> list[str]:
    token = str(product_id).strip()
    mode_token = str(mode_id).strip()
    if token in {"client", "server"}:
        ui_map = {
            "cli": "cli",
            "rendered": "gui",
            "headless": "headless",
        }
        translated = str(ui_map.get(mode_token, "")).strip()
        if translated:
            return ["--ui", translated]
    return []


def build_mode_stub(
    product_id: str,
    mode_id: str,
    command_rows: Iterable[Mapping[str, object]],
    panel_rows: Iterable[Mapping[str, object]],
) -> dict:
    token = str(mode_id).strip()
    if token == "tui":
        return build_tui_stub(product_id, command_rows, panel_rows)
    if token == "rendered":
        return build_rendered_stub(product_id)
    if token == "os_native":
        return {
            "result": "complete",
            "product_id": str(product_id).strip(),
            "mode": token,
            "status": "stub",
            "message": "APPSHELL-PLATFORM-1 native mode stub is active.",
        }
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "mode": token,
        "status": "stub",
        "message": "APPSHELL-PLATFORM-1 mode stub is active.",
    }


__all__ = [
    "build_mode_stub",
    "default_mode_for_product",
    "legacy_mode_args",
    "normalize_mode",
    "supported_modes_for_product",
]
