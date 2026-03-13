"""FAST test: DIST-3 clean-room reports are generated and complete."""

from __future__ import annotations

import os


TEST_ID = "test_clean_room_report_generated"
TEST_TAGS = ["fast", "dist", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist3_testlib import load_report

    report = load_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-3 clean-room report is missing or not complete"}
    required_paths = (
        os.path.join(repo_root, "docs", "audit", "CLEAN_ROOM_win64.md"),
        os.path.join(repo_root, "docs", "audit", "DIST3_FINAL.md"),
        os.path.join(repo_root, "data", "audit", "clean_room_win64.json"),
    )
    missing = [path for path in required_paths if not os.path.isfile(path)]
    if missing:
        return {"status": "fail", "message": "DIST-3 clean-room outputs are missing: {}".format(", ".join(sorted(missing)))}
    return {"status": "pass", "message": "DIST-3 clean-room reports are present and complete"}
