"""APPSHELL-4 TestX helpers."""

from __future__ import annotations

import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def run_probe(repo_root: str, *, suffix: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.appshell.appshell4_probe import run_ipc_attach_probe

    return run_ipc_attach_probe(repo_root, suffix=str(suffix).strip() or "default")


def replay_probe(repo_root: str, *, suffix: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.appshell.appshell4_probe import verify_ipc_attach_replay

    return verify_ipc_attach_replay(repo_root, suffix=str(suffix).strip() or "replay")
