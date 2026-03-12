"""FAST test: SOL-1 replay regenerates the same illumination-view fingerprints."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_illumination_view_fingerprint_match"
TEST_TAGS = ["fast", "sol", "illumination", "replay", "determinism"]
EXPECTED_ARTIFACT_FINGERPRINT = "26c21910c76552f2407800eb4c6786aa3bb204bd8db5c25a5eea4f417a8c7bd2"
EXPECTED_REPORT_FINGERPRINT = "9899c69a2590e143ad990ecf494e47df7d66a7a5af1a54d2029aa2763d7b543a"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.earth5_testlib import replay_report

    report = replay_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SOL-1 replay report did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "SOL-1 replay drifted across repeated runs"}
    artifact_fingerprint = str(report.get("artifact_fingerprint", "")).strip()
    if artifact_fingerprint != EXPECTED_ARTIFACT_FINGERPRINT:
        return {
            "status": "fail",
            "message": "SOL-1 artifact fingerprint drifted: expected {}, got {}".format(
                EXPECTED_ARTIFACT_FINGERPRINT,
                artifact_fingerprint,
            ),
        }
    report_fingerprint = str(report.get("deterministic_fingerprint", "")).strip()
    if report_fingerprint != EXPECTED_REPORT_FINGERPRINT:
        return {
            "status": "fail",
            "message": "SOL-1 replay report fingerprint drifted: expected {}, got {}".format(
                EXPECTED_REPORT_FINGERPRINT,
                report_fingerprint,
            ),
        }
    return {"status": "pass", "message": "SOL-1 replay reproduces the expected illumination-view fingerprints"}
