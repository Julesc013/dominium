"""FAST test: SYS-6 health aggregation is deterministic across equivalent runs."""

from __future__ import annotations

import copy
import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_health_aggregation_deterministic"
TEST_TAGS = ["fast", "system", "sys6", "reliability", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys6_testlib import base_state, execute_health_tick

    state_a = base_state()
    state_b = copy.deepcopy(state_a)

    result_a = execute_health_tick(repo_root=repo_root, state=state_a)
    result_b = execute_health_tick(repo_root=repo_root, state=state_b)
    if str(result_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first health tick did not complete"}
    if str(result_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second health tick did not complete"}

    fingerprint_a = canonical_sha256(
        {
            "hash_chain": str(state_a.get("system_health_hash_chain", "")).strip(),
            "rows": state_a.get("system_health_state_rows") or [],
        }
    )
    fingerprint_b = canonical_sha256(
        {
            "hash_chain": str(state_b.get("system_health_hash_chain", "")).strip(),
            "rows": state_b.get("system_health_state_rows") or [],
        }
    )
    if fingerprint_a != fingerprint_b:
        return {"status": "fail", "message": "system health aggregation fingerprint mismatch across equivalent runs"}
    if not str(state_a.get("system_health_hash_chain", "")).strip():
        return {"status": "fail", "message": "system_health_hash_chain missing after health tick"}
    return {"status": "pass", "message": "SYS-6 health aggregation is deterministic"}

