"""FAST test: EMB-1 canonical toolbelt session hash stays fixed across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_tool_hash_match"
TEST_TAGS = ["fast", "embodiment", "toolbelt", "cross_platform"]

EXPECTED_TOOL_SESSION_HASH = "aaa32e27dd56f2dcdb7204c5f253a3cde98e15120cf3e24e0164d0d142c02fdd"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.emb1_testlib import tool_session_report

    report = tool_session_report(repo_root)
    observed_hash = str(report.get("deterministic_fingerprint", "")).strip().lower()
    if observed_hash != EXPECTED_TOOL_SESSION_HASH:
        return {
            "status": "fail",
            "message": "EMB-1 toolbelt fingerprint drifted (expected {}, got {})".format(
                EXPECTED_TOOL_SESSION_HASH,
                observed_hash or "<missing>",
            ),
        }
    return {"status": "pass", "message": "EMB-1 canonical toolbelt fingerprint matches expected fixture"}
