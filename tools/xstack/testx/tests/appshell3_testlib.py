"""APPSHELL-3 TestX helpers."""

from __future__ import annotations

import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def build_surface(repo_root: str, *, product_id: str = "client", layout_id: str = "", backend_override: str = "lite") -> dict:
    ensure_repo_on_path(repo_root)
    from appshell.tui import build_tui_surface

    return build_tui_surface(
        repo_root,
        product_id=str(product_id).strip(),
        requested_layout_id=str(layout_id).strip(),
        backend_override=str(backend_override).strip(),
    )


def tui_source_text(repo_root: str) -> str:
    path = os.path.join(repo_root, "appshell", "tui", "tui_engine.py")
    return open(path, "r", encoding="utf-8").read()
