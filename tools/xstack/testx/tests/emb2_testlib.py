"""Shared deterministic EMB-2 locomotion fixtures for TestX."""

from __future__ import annotations

import sys


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def jump_entitlement_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.emb2_probe import jump_entitlement_report as _report

    return _report(repo_root)


def jump_grounded_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.emb2_probe import jump_grounded_report as _report

    return _report(repo_root)


def impact_event_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.emb2_probe import impact_event_report as _report

    return _report(repo_root)


def camera_smoothing_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.emb2_probe import camera_smoothing_report as _report

    return _report(repo_root)


def verify_locomotion_window_replay_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.embodiment.emb2_probe import verify_locomotion_window_replay as _report

    return _report(repo_root)


def locomotion_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    from tools.embodiment.emb2_probe import locomotion_hash as _hash

    return _hash(repo_root)
