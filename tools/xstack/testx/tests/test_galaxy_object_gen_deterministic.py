"""FAST test: GAL-1 galaxy object generation remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_galaxy_object_gen_deterministic"
TEST_TAGS = ["fast", "galaxy", "objects", "determinism"]
EXPECTED_ARTIFACT_HASH = "0e091e122f4c3bff6df710b1a01613a38452534028e734c09abb8a759765b8e0"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.gal1_testlib import galaxy_object_replay_report

    report = galaxy_object_replay_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GAL-1 replay did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "GAL-1 replay drifted across repeated runs"}
    first_run = dict(report.get("first_run") or {})
    actual_hash = str(first_run.get("artifact_hash_chain", "")).strip()
    if actual_hash != EXPECTED_ARTIFACT_HASH:
        return {
            "status": "fail",
            "message": "GAL-1 artifact hash drifted: expected {}, got {}".format(EXPECTED_ARTIFACT_HASH, actual_hash),
        }
    return {"status": "pass", "message": "GAL-1 galaxy object generation remains deterministic"}
