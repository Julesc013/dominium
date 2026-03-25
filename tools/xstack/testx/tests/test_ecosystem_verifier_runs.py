"""FAST test: the Omega ecosystem verifier runs and produces a complete report."""

from __future__ import annotations

import sys


TEST_ID = "test_ecosystem_verifier_runs"
TEST_TAGS = ["fast", "omega", "ecosystem", "smoke"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.ecosystem_verify_common import verify_ecosystem

    report = verify_ecosystem(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ecosystem verifier did not complete cleanly"}
    return {
        "status": "pass",
        "message": "ecosystem verifier completed ({})".format(str(report.get("deterministic_fingerprint", "")).strip() or "missing-fingerprint"),
    }
