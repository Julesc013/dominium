"""FAST test: SYS-3 tier hash chains remain stable across equivalent ordering variants."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_cross_platform_tier_hash_match"
TEST_TAGS = ["fast", "system", "sys3", "determinism", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.sys3_testlib import (
        base_state_two_systems,
        execute_system_roi_tick,
    )

    state_a = base_state_two_systems()
    state_b = copy.deepcopy(state_a)

    state_b["system_rows"] = list(reversed(list(state_b.get("system_rows") or [])))
    state_b["system_macro_capsule_rows"] = list(
        reversed(list(state_b.get("system_macro_capsule_rows") or []))
    )
    state_b["system_state_vector_rows"] = list(
        reversed(list(state_b.get("system_state_vector_rows") or []))
    )
    state_b["system_interface_signature_rows"] = list(
        reversed(list(state_b.get("system_interface_signature_rows") or []))
    )

    inputs = {
        "roi_system_ids": ["system.engine.beta"],
        "inspection_system_ids": [],
        "hazard_system_ids": [],
        "fidelity_request_system_ids": [],
    }
    result_a = execute_system_roi_tick(repo_root=repo_root, state=state_a, inputs=inputs)
    result_b = execute_system_roi_tick(repo_root=repo_root, state=state_b, inputs=inputs)
    if str(result_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "base SYS-3 execution failed"}
    if str(result_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reordered SYS-3 execution failed"}

    digest_a = canonical_sha256(
        {
            "tier_chain": str(state_a.get("system_tier_change_hash_chain", "")).strip(),
            "collapse_expand_chain": str(state_a.get("collapse_expand_event_hash_chain", "")).strip(),
        }
    )
    digest_b = canonical_sha256(
        {
            "tier_chain": str(state_b.get("system_tier_change_hash_chain", "")).strip(),
            "collapse_expand_chain": str(state_b.get("collapse_expand_event_hash_chain", "")).strip(),
        }
    )
    if digest_a != digest_b:
        return {"status": "fail", "message": "cross-platform SYS-3 tier hash digest diverged"}
    return {"status": "pass", "message": "cross-platform SYS-3 tier hash digest stable"}

