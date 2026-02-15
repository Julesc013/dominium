"""STRICT test: auditx changed-only scan is deterministic or returns refusal.git_unavailable."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys


TEST_ID = "testx.auditx.changed_only"
TEST_TAGS = ["strict", "auditx", "smoke"]


def _run_scan(repo_root: str, out_rel: str):
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(repo_root, "tools", "auditx", "auditx.py"),
            "scan",
            "--repo-root",
            repo_root,
            "--changed-only",
            "--format",
            "json",
            "--output-root",
            out_rel,
        ],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    return int(proc.returncode), str(proc.stdout or "")


def run(repo_root: str):
    git_available = shutil.which("git") is not None
    out_a = "build/auditx/changed_only_a"
    out_b = "build/auditx/changed_only_b"
    code_a, text_a = _run_scan(repo_root, out_a)
    if not git_available:
        if code_a != 2 or "refusal.git_unavailable" not in text_a:
            return {"status": "fail", "message": "expected refusal.git_unavailable when git is unavailable"}
        return {"status": "pass", "message": "changed-only refused deterministically without git"}

    if code_a != 0:
        tail = text_a.splitlines()[-15:]
        return {"status": "fail", "message": "changed-only scan failed: {}".format(" | ".join(tail))}

    code_b, text_b = _run_scan(repo_root, out_b)
    if code_b != 0:
        tail = text_b.splitlines()[-15:]
        return {"status": "fail", "message": "second changed-only scan failed: {}".format(" | ".join(tail))}

    path_a = os.path.join(repo_root, out_a.replace("/", os.sep), "FINDINGS.json")
    path_b = os.path.join(repo_root, out_b.replace("/", os.sep), "FINDINGS.json")
    if not os.path.isfile(path_a) or not os.path.isfile(path_b):
        return {"status": "fail", "message": "missing FINDINGS.json for changed-only scans"}
    try:
        payload_a = json.load(open(path_a, "r", encoding="utf-8"))
        payload_b = json.load(open(path_b, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid JSON in changed-only output"}
    if payload_a != payload_b:
        return {"status": "fail", "message": "changed-only scan output is not deterministic"}
    return {"status": "pass", "message": "changed-only scan determinism passed"}
