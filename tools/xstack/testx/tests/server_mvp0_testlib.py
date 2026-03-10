"""Shared fixtures for SERVER-MVP-0 TestX coverage."""

from __future__ import annotations

import os
import sys
from typing import Callable


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def boot_fixture(
    repo_root: str,
    *,
    suffix: str,
    session_mutator: Callable[[dict], dict | None] | None = None,
) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.server.server_mvp0_probe import boot_server_fixture

    return boot_server_fixture(repo_root, save_suffix=suffix, session_mutator=session_mutator)


def run_window(repo_root: str, *, suffix: str, ticks: int = 8, with_client: bool = True) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.server.server_mvp0_probe import run_server_window

    return run_server_window(repo_root, save_suffix=suffix, ticks=ticks, with_client=with_client)


def verify_replay(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.server.server_mvp0_probe import verify_server_window_replay

    return verify_server_window_replay(repo_root)


def unauthorized_report(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.server.server_mvp0_probe import unauthorized_intent_report

    return unauthorized_intent_report(repo_root)


def mutate_session_field(field_name: str, value: object):
    token = str(field_name).strip()

    def _mutator(payload: dict) -> dict:
        updated = dict(payload or {})
        updated[token] = value
        return updated

    return _mutator

