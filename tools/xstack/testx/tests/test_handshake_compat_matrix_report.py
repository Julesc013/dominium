"""STRICT test: handshake compatibility matrix report tool is deterministic."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys


TEST_ID = "testx.net.handshake_compat_matrix_report"
TEST_TAGS = ["strict", "net", "security", "multiplayer", "docs"]


def _hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _run_tool(repo_root: str):
    tool = os.path.join(repo_root, "tools", "net", "tool_handshake_matrix_report.py")
    proc = subprocess.run(
        [sys.executable, tool, "--repo-root", repo_root],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    if int(proc.returncode) != 0:
        return {}, "tool failed: {}".format(str(proc.stdout or "").strip())
    try:
        payload = json.loads(str(proc.stdout or "{}"))
    except ValueError:
        return {}, "tool output is not valid JSON"
    return payload, ""


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first, err = _run_tool(repo_root)
    if err:
        return {"status": "fail", "message": err}
    second, err = _run_tool(repo_root)
    if err:
        return {"status": "fail", "message": err}

    first_md = os.path.join(repo_root, str(first.get("out_md", "")).replace("/", os.sep))
    first_json = os.path.join(repo_root, str(first.get("out_json", "")).replace("/", os.sep))
    if not os.path.isfile(first_md) or not os.path.isfile(first_json):
        return {"status": "fail", "message": "handshake compatibility matrix outputs are missing"}

    if str(first.get("matrix_hash", "")) != str(second.get("matrix_hash", "")):
        return {"status": "fail", "message": "handshake compatibility matrix hash diverged across repeated tool runs"}
    if not _hash_file(first_md) or not _hash_file(first_json):
        return {"status": "fail", "message": "handshake compatibility output hash computation failed"}
    return {"status": "pass", "message": "handshake compatibility matrix report tool is deterministic"}
