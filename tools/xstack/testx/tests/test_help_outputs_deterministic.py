"""FAST test: DIST-5 help surfaces remain deterministic and example-driven."""

from __future__ import annotations


TEST_ID = "test_help_outputs_deterministic"
TEST_TAGS = ["fast", "dist", "release", "ux", "help"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist5_testlib import help_rows, load_report

    report = load_report(repo_root)
    rows = help_rows(report)
    if not rows:
        return {"status": "fail", "message": "DIST-5 help rows are missing"}
    for row in rows:
        if int(row.get("returncode", 0) or 0) != 0:
            return {"status": "fail", "message": "help surface failed for {}".format(str(row.get("bin_name", "")).strip())}
        if not bool(row.get("stable_across_runs")):
            return {"status": "fail", "message": "help output drifted for {}".format(str(row.get("bin_name", "")).strip())}
        if not bool(row.get("contains_examples")) or not bool(row.get("contains_tip")):
            return {"status": "fail", "message": "help guidance missing for {}".format(str(row.get("bin_name", "")).strip())}
    return {"status": "pass", "message": "DIST-5 help surfaces remain deterministic"}
