"""Shared fixtures for SERVER-MVP-1 local orchestration tests."""

from __future__ import annotations

import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def launch_spec(repo_root: str, *, suffix: str) -> dict:
    ensure_repo_on_path(repo_root)
    from src.client.local_server import build_local_server_launch_spec
    from tools.mvp.runtime_bundle import MVP_PACK_LOCK_REL, MVP_PROFILE_BUNDLE_REL

    return build_local_server_launch_spec(
        repo_root=repo_root,
        seed="0",
        profile_bundle_path=MVP_PROFILE_BUNDLE_REL,
        pack_lock_path=MVP_PACK_LOCK_REL,
        save_id="save.server_mvp1.{}".format(str(suffix).strip() or "fixture"),
    )


def run_window(repo_root: str, *, suffix: str, ticks: int = 6) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.server.server_mvp1_probe import run_local_singleplayer_window

    return run_local_singleplayer_window(repo_root, save_suffix=suffix, ticks=ticks)


def verify_replay(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.server.server_mvp1_probe import verify_local_singleplayer_replay

    return verify_local_singleplayer_replay(repo_root)


def crash_diag(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.server.server_mvp1_probe import crash_diag_report

    return crash_diag_report(repo_root)
