"""FAST test: release-index policy fixture resolution is deterministic across repeated runs."""

from __future__ import annotations

import json


TEST_ID = "test_resolution_deterministic_across_runs"
TEST_TAGS = ["fast", "release", "release-index-policy", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.release_index_policy_testlib import build_report

    left = build_report(repo_root)
    right = build_report(repo_root)
    if str(left.get("deterministic_fingerprint", "")).strip() != str(right.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "release-index policy report fingerprint drifted across repeated runs"}
    if json.dumps(left, sort_keys=True) != json.dumps(right, sort_keys=True):
        return {"status": "fail", "message": "release-index policy payload drifted across repeated runs"}
    if not bool(left.get("determinism_replay_match")):
        return {"status": "fail", "message": "policy report recorded a determinism replay mismatch"}
    return {"status": "pass", "message": "release-index policy resolution is deterministic across repeated runs"}
