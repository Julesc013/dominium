"""FAST test: SYS-2 capsule execution produces deterministic replay-equal results."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_capsule_execution_deterministic"
TEST_TAGS = ["fast", "system", "sys2", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.sys2_testlib import (
        base_state,
        execute_macro_tick,
        policy_context_for_macro,
    )

    policy_context = policy_context_for_macro(repo_root=repo_root)
    state_a = base_state()
    state_b = copy.deepcopy(state_a)

    result_a = execute_macro_tick(state=state_a, repo_root=repo_root, inputs={}, policy_context=policy_context)
    result_b = execute_macro_tick(state=state_b, repo_root=repo_root, inputs={}, policy_context=policy_context)
    if str(result_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first macro tick execution did not complete"}
    if str(result_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second macro tick execution did not complete"}

    fingerprint_a = canonical_sha256(
        {
            "runtime": str(state_a.get("system_macro_runtime_hash_chain", "")).strip(),
            "forced": str(state_a.get("system_forced_expand_event_hash_chain", "")).strip(),
            "output": str(state_a.get("system_macro_output_record_hash_chain", "")).strip(),
            "flow_adjust": state_a.get("model_flow_adjustment_rows") or [],
        }
    )
    fingerprint_b = canonical_sha256(
        {
            "runtime": str(state_b.get("system_macro_runtime_hash_chain", "")).strip(),
            "forced": str(state_b.get("system_forced_expand_event_hash_chain", "")).strip(),
            "output": str(state_b.get("system_macro_output_record_hash_chain", "")).strip(),
            "flow_adjust": state_b.get("model_flow_adjustment_rows") or [],
        }
    )
    if fingerprint_a != fingerprint_b:
        return {"status": "fail", "message": "macro capsule execution fingerprint changed across equivalent runs"}
    return {"status": "pass", "message": "macro capsule execution deterministic fingerprint stable"}

