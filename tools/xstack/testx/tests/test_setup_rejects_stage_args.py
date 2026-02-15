"""STRICT test: setup/build refuses pipeline stage-driving arguments."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.setup.rejects_stage_args"
TEST_TAGS = ["strict", "bundle", "session"]


def run(repo_root: str):
    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "setup", "build.py"),
        "--bundle",
        "bundle.base.lab",
        "--out",
        "build/dist.testx.setup.guard",
        "--to-stage",
        "stage.session_running",
    ]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        encoding="utf-8",
    )
    if int(proc.returncode) != 2:
        return {"status": "fail", "message": "setup/build should return refusal exit code for stage args"}
    stdout = str(proc.stdout or "").strip()
    if not stdout:
        return {"status": "fail", "message": "setup/build refusal output missing"}
    try:
        payload = json.loads(stdout)
    except ValueError:
        return {"status": "fail", "message": "setup/build refusal output is not valid JSON"}
    if str(payload.get("result", "")) != "refused":
        return {"status": "fail", "message": "setup/build should return result=refused for stage args"}
    reason_code = str((payload.get("refusal") or {}).get("reason_code", ""))
    if reason_code != "REFUSE_SETUP_PIPELINE_FORBIDDEN":
        return {"status": "fail", "message": "expected REFUSE_SETUP_PIPELINE_FORBIDDEN, got '{}'".format(reason_code)}
    return {"status": "pass", "message": "setup/build stage-argument refusal check passed"}
