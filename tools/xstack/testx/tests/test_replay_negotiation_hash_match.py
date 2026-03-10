"""FAST test: CAP-NEG-2 negotiation replay tool emits stable hashes."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "test_replay_negotiation_hash_match"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def _run_tool(repo_root: str, output_rel: str) -> dict:
    tool_abs = os.path.join(repo_root, "tools", "compat", "tool_replay_negotiation.py")
    output_abs = os.path.join(repo_root, output_rel)
    completed = subprocess.run(
        [sys.executable, tool_abs, "--repo-root", repo_root, "--output-path", output_abs],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if int(completed.returncode or 0) != 0:
        return {"result": "refused", "stdout": str(completed.stdout or ""), "stderr": str(completed.stderr or "")}
    return json.loads(str(completed.stdout or "{}"))


def run(repo_root: str):
    first = _run_tool(repo_root, os.path.join("build", "cap_neg2_tests", "replay_a.json"))
    second = _run_tool(repo_root, os.path.join("build", "cap_neg2_tests", "replay_b.json"))
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "negotiation replay tool did not complete"}
    if str(first.get("negotiation_record_hash", "")) != str(second.get("negotiation_record_hash", "")):
        return {"status": "fail", "message": "negotiation replay hash drifted across repeated runs"}
    if str((dict(first.get("verification") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "negotiation replay verification did not complete"}
    return {"status": "pass", "message": "negotiation replay hash is stable"}
