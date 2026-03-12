"""FAST test: GAL-0 galaxy proxy replay remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_galaxy_proxy_fields_deterministic"
TEST_TAGS = ["fast", "galaxy", "proxy", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.gal0_testlib import galaxy_proxy_replay_report

    report = galaxy_proxy_replay_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GAL-0 galaxy proxy replay did not complete"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "GAL-0 galaxy proxy replay drifted across repeated runs"}
    return {"status": "pass", "message": "GAL-0 galaxy proxy replay is deterministic"}
