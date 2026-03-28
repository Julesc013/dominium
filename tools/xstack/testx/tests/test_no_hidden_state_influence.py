"""FAST test: SYS0 collapse output is insensitive to unrelated hidden state noise."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_no_hidden_state_influence"
TEST_TAGS = ["fast", "system", "sys0", "determinism", "hidden_state"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system.system_collapse_engine import collapse_system_graph
    from tools.xstack.testx.tests.sys0_testlib import cloned_state, validation_registry_payloads

    state_a = cloned_state()
    state_b = copy.deepcopy(cloned_state())
    state_b["ui_temp_cache"] = {"nondiegetic_panel": "ignored"}
    state_b["debug_overlay_tokens"] = ["alpha", "beta"]
    registry_payloads = validation_registry_payloads(repo_root=repo_root)
    collapse_payloads = {
        key: registry_payloads[key]
        for key in (
            "quantity_bundle_registry_payload",
            "spec_type_registry_payload",
            "signal_channel_type_registry_payload",
            "boundary_invariant_template_registry_payload",
            "tolerance_policy_registry_payload",
            "safety_pattern_registry_payload",
        )
    }

    first = collapse_system_graph(
        state=state_a,
        system_id="system.engine.alpha",
        current_tick=0,
        process_id="process.system_collapse",
        **collapse_payloads,
    )
    second = collapse_system_graph(
        state=state_b,
        system_id="system.engine.alpha",
        current_tick=0,
        process_id="process.system_collapse",
        **collapse_payloads,
    )

    fingerprint_a = str(first.get("deterministic_fingerprint", "")).strip()
    fingerprint_b = str(second.get("deterministic_fingerprint", "")).strip()
    if (not fingerprint_a) or (not fingerprint_b):
        return {"status": "fail", "message": "collapse deterministic fingerprint missing"}
    if fingerprint_a != fingerprint_b:
        return {"status": "fail", "message": "collapse fingerprint changed due to unrelated hidden state"}

    if str(first.get("provenance_anchor_hash", "")).strip() != str(second.get("provenance_anchor_hash", "")).strip():
        return {"status": "fail", "message": "provenance anchor changed due to unrelated hidden state"}

    return {"status": "pass", "message": "no hidden state influence on collapse boundary behavior"}
