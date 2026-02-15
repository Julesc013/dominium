"""Smoke test: tools/xstack/run fast produces tools/xstack/out/fast/latest/report.json."""

from __future__ import annotations

import json
import os
import subprocess
import sys


TEST_ID = "testx.smoke.run_fast_report"
TEST_TAGS = ["smoke", "runner"]


def run(repo_root: str):
    report_rel = "tools/xstack/out/fast/latest/report.json"
    report_path = os.path.join(repo_root, report_rel.replace("/", os.sep))
    if os.path.isfile(report_path):
        try:
            os.remove(report_path)
        except OSError:
            pass

    env = dict(os.environ)
    env["DOM_XSTACK_SKIP_TESTX"] = "1"
    proc = subprocess.run(
        [sys.executable, os.path.join(repo_root, "tools", "xstack", "run.py"), "fast", "--cache", "on"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env,
        check=False,
    )
    if int(proc.returncode) != 0:
        output_tail = (proc.stdout or "").splitlines()[-15:]
        return {
            "status": "fail",
            "message": "nested run.py fast failed: {}".format(" | ".join(output_tail)),
        }
    if not os.path.isfile(report_path):
        return {
            "status": "fail",
            "message": "missing report artifact '{}'".format(report_rel),
        }
    try:
        payload = json.load(open(report_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {
            "status": "fail",
            "message": "invalid JSON in '{}'".format(report_rel),
        }
    if str(payload.get("profile", "")).upper() != "FAST":
        return {
            "status": "fail",
            "message": "report profile must be FAST",
        }
    return {
        "status": "pass",
        "message": "fast report artifact produced and readable",
    }

