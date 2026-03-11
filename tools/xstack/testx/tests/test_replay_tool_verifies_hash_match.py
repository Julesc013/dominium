"""FAST test: DIAG-0 replay tool verifies bundle hash equivalence offline."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "test_replay_tool_verifies_hash_match"
TEST_TAGS = ["fast", "diag", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.diag0_testlib import cleanup_temp_dir, capture_bundle, make_temp_dir

    temp_dir = make_temp_dir("diag0_replay_")
    try:
        capture = capture_bundle(repo_root, out_dir=temp_dir, include_views=True)
        tool_abs = os.path.join(repo_root, "tools", "diag", "tool_replay_bundle.py")
        completed = subprocess.run(
            [
                sys.executable,
                tool_abs,
                "--repo-root",
                repo_root,
                "--bundle-path",
                str(capture.get("bundle_dir", "")),
                "--tick-window",
                "16",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if int(completed.returncode or 0) != 0:
            return {"status": "fail", "message": "replay tool returned non-zero"}
        payload = json.loads(str(completed.stdout or "{}"))
        replay_result = dict(payload.get("replay_result") or {})
        if str(payload.get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "replay tool did not complete"}
        if not bool(replay_result.get("hash_match", False)):
            return {"status": "fail", "message": "replay tool reported a hash mismatch"}
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "replay tool verifies deterministic repro bundle hashes"}
