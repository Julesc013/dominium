"""FAST test: developer acceleration CLI exposes required Prompt 19 commands."""

from __future__ import annotations

import os
import subprocess
import sys


TEST_ID = "testx.dev.commands_exist"
TEST_TAGS = ["smoke", "tools", "runner"]


def _run(repo_root: str, argv):
    return subprocess.run(
        argv,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def run(repo_root: str):
    cli = [sys.executable, os.path.join(repo_root, "tools", "dev", "dev.py"), "--repo-root", "."]
    top = _run(repo_root, cli + ["--help"])
    if int(top.returncode) != 0:
        return {"status": "fail", "message": "tools/dev/dev.py --help failed"}
    top_text = str(top.stdout or "")
    for token in (
        "impact-graph",
        "impacted-tests",
        "impacted-build",
        "run",
        "audit",
        "verify",
        "profile",
    ):
        if token not in top_text:
            return {"status": "fail", "message": "missing top-level dev command '{}'".format(token)}

    run_help = _run(repo_root, cli + ["run", "--help"])
    if int(run_help.returncode) != 0:
        return {"status": "fail", "message": "tools/dev/dev.py run --help failed"}
    run_text = str(run_help.stdout or "")
    for token in ("observer", "galaxy", "sol", "earth"):
        if token not in run_text:
            return {"status": "fail", "message": "missing run target '{}'".format(token)}
    return {"status": "pass", "message": "developer CLI command surface exists"}
