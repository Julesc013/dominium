"""STRICT test: auditx scan does not mutate tracked runtime files."""

from __future__ import annotations

import os
import subprocess
import sys


TEST_ID = "testx.auditx.read_only"
TEST_TAGS = ["strict", "auditx", "smoke"]


RUNTIME_PREFIXES = (
    "engine/",
    "game/",
    "client/",
    "server/",
    "launcher/",
    "setup/",
    "libs/",
)


def _tracked_runtime_status(repo_root: str):
    proc = subprocess.run(
        ["git", "status", "--porcelain", "-uall"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        return None, "git status failed"
    rows = []
    for line in (proc.stdout or "").splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip() if len(line) >= 3 else line.strip()
        path = path.replace("\\", "/")
        if not path.startswith(RUNTIME_PREFIXES):
            continue
        if status == "??":
            continue
        rows.append((status, path))
    return sorted(rows), ""


def run(repo_root: str):
    before, err = _tracked_runtime_status(repo_root)
    if err:
        return {"status": "fail", "message": err}

    out_rel = ".xstack_cache/auditx/read_only_test"
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
    if int(proc.returncode) not in (0, 2):
        tail = (proc.stdout or "").splitlines()[-15:]
        return {"status": "fail", "message": "auditx read-only scan failed: {}".format(" | ".join(tail))}

    after, err = _tracked_runtime_status(repo_root)
    if err:
        return {"status": "fail", "message": err}
    if before != after:
        return {"status": "fail", "message": "auditx scan modified tracked runtime files"}
    return {"status": "pass", "message": "auditx scan preserved tracked runtime file status"}
