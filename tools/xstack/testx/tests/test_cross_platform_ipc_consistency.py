"""FAST test: AppShell IPC framing and attach hashes remain stable across repeated runs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_ipc_consistency"
TEST_TAGS = ["fast", "appshell", "ipc", "cross_platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell4_testlib import replay_probe

    report = replay_probe(repo_root, suffix="ipc_unify_cross_platform")
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "IPC replay probe reported mismatches: {}".format(", ".join(list(report.get("mismatches") or [])))}
    first = dict(report.get("first") or {})
    second = dict(report.get("second") or {})
    if str(first.get("cross_platform_ipc_hash", "")).strip() != str(second.get("cross_platform_ipc_hash", "")).strip():
        return {"status": "fail", "message": "cross-platform IPC hash drifted across repeated runs"}
    return {"status": "pass", "message": "IPC attach and framing hashes remain stable across repeated runs"}
