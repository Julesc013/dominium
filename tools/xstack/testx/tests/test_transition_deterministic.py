"""FAST test: SYS-3 tier transitions are deterministic across equivalent runs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_transition_deterministic"
TEST_TAGS = ["fast", "system", "sys3", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.sys3_testlib import (
        base_state_two_systems,
        execute_system_roi_tick,
    )

    inputs = {
        "roi_system_ids": ["system.engine.beta"],
        "max_expands_per_tick": 8,
        "max_collapses_per_tick": 8,
    }
    state_a = base_state_two_systems()
    state_b = copy.deepcopy(state_a)

    state_b["system_rows"] = list(reversed(list(state_b.get("system_rows") or [])))
    state_b["system_interface_signature_rows"] = list(
        reversed(list(state_b.get("system_interface_signature_rows") or []))
    )
    state_b["assembly_rows"] = list(reversed(list(state_b.get("assembly_rows") or [])))

    result_a = execute_system_roi_tick(repo_root=repo_root, state=state_a, inputs=inputs)
    result_b = execute_system_roi_tick(repo_root=repo_root, state=state_b, inputs=inputs)
    if str(result_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first SYS-3 transition run did not complete"}
    if str(result_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second SYS-3 transition run did not complete"}

    digest_a = canonical_sha256(
        {
            "tier": str(state_a.get("system_tier_change_hash_chain", "")).strip(),
            "collapse_expand": str(state_a.get("collapse_expand_event_hash_chain", "")).strip(),
            "tiers": sorted(
                [
                    {
                        "system_id": str(row.get("system_id", "")).strip(),
                        "current_tier": str(row.get("current_tier", "")).strip(),
                        "active_capsule_id": str(row.get("active_capsule_id", "")).strip(),
                    }
                    for row in list(state_a.get("system_rows") or [])
                    if isinstance(row, dict)
                ],
                key=lambda row: str(row.get("system_id", "")),
            ),
        }
    )
    digest_b = canonical_sha256(
        {
            "tier": str(state_b.get("system_tier_change_hash_chain", "")).strip(),
            "collapse_expand": str(state_b.get("collapse_expand_event_hash_chain", "")).strip(),
            "tiers": sorted(
                [
                    {
                        "system_id": str(row.get("system_id", "")).strip(),
                        "current_tier": str(row.get("current_tier", "")).strip(),
                        "active_capsule_id": str(row.get("active_capsule_id", "")).strip(),
                    }
                    for row in list(state_b.get("system_rows") or [])
                    if isinstance(row, dict)
                ],
                key=lambda row: str(row.get("system_id", "")),
            ),
        }
    )
    if digest_a != digest_b:
        return {"status": "fail", "message": "SYS-3 transition digest drifted across equivalent input orderings"}
    return {"status": "pass", "message": "SYS-3 transition path deterministic across equivalent runs"}

