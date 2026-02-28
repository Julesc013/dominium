"""FAST test: direct intent dispatch paths remain whitelist-restricted."""

from __future__ import annotations

import sys


TEST_ID = "test_direct_dispatch_blocked"
TEST_TAGS = ["fast", "architecture", "control"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.test_no_direct_intent_dispatch import run as run_no_direct_dispatch

    result = run_no_direct_dispatch(repo_root)
    if str(result.get("status", "")) != "pass":
        return {
            "status": "fail",
            "message": str(result.get("message", "direct dispatch check failed")),
        }
    return {"status": "pass", "message": "direct dispatch remains blocked outside control/net ingress"}
