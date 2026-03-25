"""Shared UPDATE-SIM-0 TestX helpers."""

from __future__ import annotations

import os

from tools.mvp.update_sim_common import load_update_sim_baseline, run_update_sim
from tools.xstack.compatx.canonical_json import canonical_json_text


def build_report(repo_root: str, *, suffix: str) -> dict:
    root = os.path.abspath(repo_root)
    return run_update_sim(
        root,
        output_root_rel=os.path.join("build", "tmp", "testx_update_sim", suffix),
        write_outputs=False,
    )


def committed_baseline(repo_root: str) -> dict:
    return load_update_sim_baseline(os.path.abspath(repo_root))


def reports_match(repo_root: str, *, left_suffix: str, right_suffix: str) -> bool:
    left = build_report(repo_root, suffix=left_suffix)
    right = build_report(repo_root, suffix=right_suffix)
    return canonical_json_text(left) == canonical_json_text(right)


__all__ = ["build_report", "committed_baseline", "reports_match"]
