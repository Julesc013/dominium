"""Shared Ω-10 DIST final plan TestX helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from tools.release.dist_final_common import (
    DIST_FINAL_CHECKLIST_DOC_REL,
    DIST_FINAL_DRYRUN_DOC_REL,
    DIST_FINAL_EXPECTED_ARTIFACTS_REL,
    DIST_FINAL_PLAN_DOC_REL,
    load_expected_artifacts,
)


def required_plan_paths() -> list[str]:
    return [
        DIST_FINAL_PLAN_DOC_REL,
        DIST_FINAL_CHECKLIST_DOC_REL,
        DIST_FINAL_EXPECTED_ARTIFACTS_REL,
        DIST_FINAL_DRYRUN_DOC_REL,
    ]


def committed_expected_artifacts(repo_root: str) -> dict:
    return load_expected_artifacts(os.path.abspath(repo_root))


def run_dryrun_tool(repo_root: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    proc = subprocess.run(
        [sys.executable, os.path.join(repo_root, "tools", "release", "tool_dist_final_dryrun.py"), "--repo-root", "."],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    payload: dict = {}
    try:
        candidate = json.loads(str(proc.stdout or "").strip())
    except ValueError:
        candidate = {}
    if isinstance(candidate, dict):
        payload = candidate
    return proc, payload


__all__ = [
    "committed_expected_artifacts",
    "required_plan_paths",
    "run_dryrun_tool",
]
