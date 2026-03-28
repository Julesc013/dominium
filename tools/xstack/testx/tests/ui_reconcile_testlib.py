"""Helpers for UI-RECONCILE-0 TestX coverage."""

from __future__ import annotations

import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def build_report(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.release.ui_reconcile_common import build_ui_reconcile_report

    return build_ui_reconcile_report(repo_root)


def violations(repo_root: str) -> list[dict]:
    ensure_repo_on_path(repo_root)
    from tools.release.ui_reconcile_common import ui_reconcile_violations

    return list(ui_reconcile_violations(repo_root))


def build_client_menu_surface(repo_root: str, *, current_state_id: str = "", seed_value: str = "") -> dict:
    ensure_repo_on_path(repo_root)
    from client.ui.main_menu_surface import build_client_main_menu_surface

    return build_client_main_menu_surface(
        repo_root=repo_root,
        current_state_id=current_state_id,
        seed_value=seed_value,
    )

