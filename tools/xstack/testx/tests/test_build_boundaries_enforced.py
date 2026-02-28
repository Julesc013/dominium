"""FAST test: build boundary scanner must pass and remain deterministic."""

from __future__ import annotations

import os
import subprocess
import sys


TEST_ID = "test_build_boundaries_enforced"
TEST_TAGS = ["fast", "architecture", "boundary"]


def run(repo_root: str):
    script_path = os.path.join(repo_root, "scripts", "verify_build_target_boundaries.py")
    if not os.path.isfile(script_path):
        return {"status": "fail", "message": "missing boundary verification script"}

    proc = subprocess.run(
        [sys.executable, script_path, "--repo-root", repo_root],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        return {
            "status": "fail",
            "message": "boundary verification failed: {}".format(str(proc.stdout or "").strip()[:400]),
        }
    return {"status": "pass", "message": "build boundary scanner passed"}
