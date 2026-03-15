"""FAST test: built Tier 1 targets pass convergence, clean-room, and DIST-4 gates."""

from __future__ import annotations


TEST_ID = "test_tier1_targets_pass_gates"
TEST_TAGS = ["fast", "release", "platform", "arch-matrix", "gate"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_matrix_testlib import build_report

    rows = list(dict(build_report(repo_root)).get("tier1_gate_rows") or [])
    if not rows:
        return {"status": "fail", "message": "ARCH-MATRIX must report at least one built Tier 1 target gate row"}
    for row in rows:
        row_map = dict(row or {})
        if str(row_map.get("result", "")).strip() == "complete":
            continue
        return {
            "status": "fail",
            "message": "Tier 1 target '{}' did not pass all required gates".format(str(row_map.get("target_id", "")).strip() or "unknown"),
        }
    return {"status": "pass", "message": "all built Tier 1 targets passed required gates"}
