"""FAST test: impacted-tests CLI output is deterministic for fixed input."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.dev.commands_deterministic"
TEST_TAGS = ["smoke", "tools", "runner"]


def _invoke(repo_root: str):
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(repo_root, "tools", "dev", "dev.py"),
            "--repo-root",
            ".",
            "impacted-tests",
            "--changed-files",
            "schemas/session_spec.schema.json",
            "--out",
            "build/impact_graph.test.det.json",
        ],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        return {}, "dev impacted-tests command failed"
    try:
        payload = json.loads(str(proc.stdout or ""))
    except ValueError:
        return {}, "dev impacted-tests output is not valid JSON"
    if not isinstance(payload, dict):
        return {}, "dev impacted-tests output root must be object"
    return payload, ""


def run(repo_root: str):
    first, err = _invoke(repo_root)
    if err:
        return {"status": "fail", "message": err}
    second, err = _invoke(repo_root)
    if err:
        return {"status": "fail", "message": err}
    if first != second:
        return {"status": "fail", "message": "dev impacted-tests output is non-deterministic"}
    if not list(first.get("impacted_test_ids") or []):
        return {"status": "fail", "message": "expected non-empty impacted_test_ids"}
    return {"status": "pass", "message": "developer CLI deterministic output passed"}
