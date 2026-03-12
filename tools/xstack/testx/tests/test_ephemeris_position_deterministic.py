"""FAST test: SOL-2 ephemeris proxy positions remain deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_ephemeris_position_deterministic"
TEST_TAGS = ["fast", "sol", "orbit", "ephemeris", "determinism"]
EXPECTED_POSITION_HASH = "c43509fc8bfd55d640deb8e34d08f625585601320d3cd037dff8c826d280048c"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sol2_testlib import orbit_replay_report_payload

    report = orbit_replay_report_payload(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SOL-2 orbit replay did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "SOL-2 ephemeris positions drifted across repeated runs"}
    if str(report.get("system_chart_mode", "")).strip() != "system":
        return {"status": "fail", "message": "SOL-2 system chart mode drifted"}
    if str(report.get("earth_chart_mode", "")).strip() != "planet_local":
        return {"status": "fail", "message": "SOL-2 earth-local chart mode drifted"}
    actual_hash = str(report.get("position_hash", "")).strip()
    if actual_hash != EXPECTED_POSITION_HASH:
        return {
            "status": "fail",
            "message": "SOL-2 position hash drifted: expected {}, got {}".format(EXPECTED_POSITION_HASH, actual_hash),
        }
    return {"status": "pass", "message": "SOL-2 ephemeris proxy positions remain deterministic"}
