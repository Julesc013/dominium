"""IPC-UNIFY-0 TestX helpers."""

from __future__ import annotations

import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def build_report(repo_root: str, *, include_runtime: bool = False) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.appshell.ipc_unify_common import build_ipc_unify_report

    return build_ipc_unify_report(repo_root, include_runtime=include_runtime)
