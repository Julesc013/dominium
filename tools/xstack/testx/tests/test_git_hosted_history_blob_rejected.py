"""FAST test: RepoX rejects oversized hosted-remote blobs that survive only in local history."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile


TEST_ID = "test_git_hosted_history_blob_rejected"
TEST_TAGS = ["fast", "repox", "git", "artifact_budget"]


def _run_git(repo_root: str, *args: str):
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox import check as repox_check

    temp_root = tempfile.mkdtemp(prefix="xstack_repox_git_history_blob_")
    origin_root = tempfile.mkdtemp(prefix="xstack_repox_git_history_blob_origin_")
    original_limit = int(repox_check.GIT_HOSTED_BLOB_HARD_LIMIT_BYTES)
    try:
        proc = _run_git(origin_root, "init", "--bare")
        if int(proc.returncode) != 0:
            return {"status": "fail", "message": "failed to init bare origin: {}".format(proc.stderr.strip())}

        proc = _run_git(temp_root, "init", "-b", "main")
        if int(proc.returncode) != 0:
            return {"status": "fail", "message": "failed to init temp repo: {}".format(proc.stderr.strip())}

        for key, value in (("user.name", "Codex"), ("user.email", "codex@example.invalid")):
            proc = _run_git(temp_root, "config", key, value)
            if int(proc.returncode) != 0:
                return {
                    "status": "fail",
                    "message": "failed to configure git {}: {}".format(key, proc.stderr.strip()),
                }

        base_path = os.path.join(temp_root, "README.md")
        with open(base_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("base\n")

        for args in (("add", "README.md"), ("commit", "-m", "base"), ("remote", "add", "origin", origin_root)):
            proc = _run_git(temp_root, *args)
            if int(proc.returncode) != 0:
                return {"status": "fail", "message": "git {} failed: {}".format(" ".join(args), proc.stderr.strip())}

        proc = _run_git(temp_root, "push", "-u", "origin", "main")
        if int(proc.returncode) != 0:
            return {"status": "fail", "message": "failed to seed origin/main: {}".format(proc.stderr.strip())}

        large_rel = os.path.join("docs", "audit", "too_large_history_blob.json")
        large_abs = os.path.join(temp_root, large_rel)
        os.makedirs(os.path.dirname(large_abs), exist_ok=True)
        with open(large_abs, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("x" * 2048)

        for args in (("add", large_rel), ("commit", "-m", "add too-large blob")):
            proc = _run_git(temp_root, *args)
            if int(proc.returncode) != 0:
                return {"status": "fail", "message": "git {} failed: {}".format(" ".join(args), proc.stderr.strip())}

        os.remove(large_abs)
        for args in (("rm", large_rel), ("commit", "-m", "remove too-large blob")):
            proc = _run_git(temp_root, *args)
            if int(proc.returncode) != 0:
                return {"status": "fail", "message": "git {} failed: {}".format(" ".join(args), proc.stderr.strip())}

        repox_check.GIT_HOSTED_BLOB_HARD_LIMIT_BYTES = 1024
        result = repox_check.run_repox_check(repo_root=temp_root, profile="STRICT")
        findings = [dict(row) for row in list(result.get("findings") or []) if isinstance(row, dict)]
        for row in findings:
            if str(row.get("rule_id", "")).strip() != "INV-GIT-HOSTED-HISTORY-BLOB-SIZE":
                continue
            file_path = str(row.get("file_path", "")).replace("\\", "/")
            if file_path.endswith("docs/audit/too_large_history_blob.json"):
                return {
                    "status": "pass",
                    "message": "RepoX rejects oversized hosted-remote blobs that remain only in outgoing history",
                }
        return {
            "status": "fail",
            "message": "expected INV-GIT-HOSTED-HISTORY-BLOB-SIZE finding for removed oversized history blob",
        }
    finally:
        repox_check.GIT_HOSTED_BLOB_HARD_LIMIT_BYTES = original_limit
        shutil.rmtree(temp_root, ignore_errors=True)
        shutil.rmtree(origin_root, ignore_errors=True)
