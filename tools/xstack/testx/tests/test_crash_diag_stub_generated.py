"""FAST test: SERVER-MVP-1 crash supervision emits a diag stub."""

from __future__ import annotations

import os


TEST_ID = "test_crash_diag_stub_generated"
TEST_TAGS = ["fast", "server", "singleplayer"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp1_testlib import crash_diag

    report = crash_diag(repo_root)
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "crash diag probe did not complete"}
    if int(report.get("exit_code", 0) or 0) != 17:
        return {"status": "fail", "message": "expected deterministic crash probe exit code 17"}
    diag_rel = str(report.get("diag_stub_path", "")).strip()
    if not diag_rel or not os.path.isfile(os.path.join(repo_root, diag_rel.replace("/", os.sep))):
        return {"status": "fail", "message": "local crash diag stub was not generated"}
    return {"status": "pass", "message": "SERVER-MVP-1 crash supervision emits a deterministic diag stub"}
