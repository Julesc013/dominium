"""FAST test: SOL-1 phase geometry hashes remain stable across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_phase_deterministic_across_platforms"
TEST_TAGS = ["fast", "sol", "illumination", "cross_platform", "hash"]
EXPECTED_GEOMETRY_FINGERPRINT = "0b252622a31bae629a66d9c4bdeecb1ff27348c4ac2633c649ac76d2fe0a1ce8"
EXPECTED_WINDOW_HASH = "217f853b386a5a48fcba79f56ed7ff9b1cc32b9ce495e3ee1c8eb1ff6dbef783"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.earth5_testlib import replay_report

    report = replay_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SOL-1 illumination replay report did not complete"}
    geometry_fingerprint = str(report.get("geometry_fingerprint", "")).strip()
    if geometry_fingerprint != EXPECTED_GEOMETRY_FINGERPRINT:
        return {
            "status": "fail",
            "message": "SOL-1 geometry fingerprint drifted: expected {}, got {}".format(
                EXPECTED_GEOMETRY_FINGERPRINT,
                geometry_fingerprint,
            ),
        }
    geometry_window_hash = str(report.get("geometry_window_hash", "")).strip()
    if geometry_window_hash != EXPECTED_WINDOW_HASH:
        return {
            "status": "fail",
            "message": "SOL-1 geometry window hash drifted: expected {}, got {}".format(
                EXPECTED_WINDOW_HASH,
                geometry_window_hash,
            ),
        }
    return {"status": "pass", "message": "SOL-1 phase geometry hashes match deterministic cross-platform fixtures"}
