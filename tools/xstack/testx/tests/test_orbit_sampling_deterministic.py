"""FAST test: SOL-2 orbit-path sampling remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_orbit_sampling_deterministic"
TEST_TAGS = ["fast", "sol", "orbit", "sampling", "determinism"]
EXPECTED_SAMPLING_HASH = "b494bde2a2342f6f82dd48d8199b692b0f38142255b5543c8bbd7cb439a0ffb8"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sol2_testlib import orbit_replay_report_payload

    report = orbit_replay_report_payload(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SOL-2 orbit replay did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "SOL-2 orbit sampling drifted across repeated runs"}
    actual_hash = str(report.get("sampling_hash", "")).strip()
    if actual_hash != EXPECTED_SAMPLING_HASH:
        return {
            "status": "fail",
            "message": "SOL-2 sampling hash drifted: expected {}, got {}".format(EXPECTED_SAMPLING_HASH, actual_hash),
        }
    return {"status": "pass", "message": "SOL-2 orbit-path sampling remains deterministic"}
