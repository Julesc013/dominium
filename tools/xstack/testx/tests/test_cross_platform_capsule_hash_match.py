"""FAST test: SYS0 capsule hashes are deterministic across equivalent runs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_cross_platform_capsule_hash_match"
TEST_TAGS = ["fast", "system", "sys0", "determinism", "hash"]


def _collapse_summary(state: dict) -> dict:
    from tools.xstack.testx.tests.sys0_testlib import execute_system_process

    result = execute_system_process(
        state=state,
        process_id="process.system_collapse",
        inputs={"system_id": "system.engine.alpha"},
    )
    return {
        "result": str(result.get("result", "")).strip(),
        "capsule_id": str(result.get("capsule_id", "")).strip(),
        "state_vector_id": str(result.get("state_vector_id", "")).strip(),
        "provenance_anchor_hash": str(result.get("provenance_anchor_hash", "")).strip(),
        "deterministic_fingerprint": str(result.get("deterministic_fingerprint", "")).strip(),
        "system_collapse_hash_chain": str(result.get("system_collapse_hash_chain", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys0_testlib import cloned_state

    first = _collapse_summary(cloned_state())
    second = _collapse_summary(copy.deepcopy(cloned_state()))

    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "collapse refused unexpectedly while computing hash summaries"}
    if first != second:
        return {"status": "fail", "message": "capsule hash summary diverged across equivalent runs"}

    return {"status": "pass", "message": "cross-platform capsule hash summary stable"}
