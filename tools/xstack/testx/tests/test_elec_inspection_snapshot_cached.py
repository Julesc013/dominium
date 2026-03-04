"""FAST test: ELEC-4 inspection snapshots are cached deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_elec_inspection_snapshot_cached"
TEST_TAGS = ["fast", "electric", "inspection", "cache"]


def _inspection_cache_policy() -> dict:
    return {
        "cache_policy_id": "cache.default",
        "enable_caching": True,
        "invalidation_rules": ["invalidate.on_target_truth_hash_change"],
        "max_cache_entries": 64,
        "eviction_rule_id": "evict.deterministic_lru",
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context,
        base_state,
        build_power_graph,
        law_profile,
        model_binding_rows,
        policy_context,
    )

    state = base_state(current_tick=40)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=300, resistance_proxy=7)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=110, motor_demand_p=70, motor_pf_permille=900)

    law = copy.deepcopy(law_profile(["process.elec.network_tick", "process.inspect_generate_snapshot"]))
    law["process_entitlement_requirements"] = dict(law.get("process_entitlement_requirements") or {})
    law["process_privilege_requirements"] = dict(law.get("process_privilege_requirements") or {})
    law["process_entitlement_requirements"]["process.inspect_generate_snapshot"] = "entitlement.inspect"
    law["process_privilege_requirements"]["process.inspect_generate_snapshot"] = "observer"

    authority = copy.deepcopy(authority_context())
    authority["privilege_level"] = "observer"

    policy = copy.deepcopy(policy_context(e1_enabled=True))
    policy["inspection_cache_policy_id"] = "cache.default"
    policy["inspection_cache_policy_registry"] = {"policies": [_inspection_cache_policy()]}

    tick_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.inspect.cache.tick.001",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(tick_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed for electrical inspection cache fixture"}

    inspect_inputs = {"target_id": "graph.elec.main", "desired_fidelity": "meso", "max_cost_units": 2}
    first = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.inspect.cache.001",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": dict(inspect_inputs),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.inspect.cache.002",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": dict(inspect_inputs),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "inspection snapshot generation failed for electrical cache fixture"}
    if bool(first.get("cache_hit", False)):
        return {"status": "fail", "message": "first electrical inspection snapshot should be cache miss"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "second electrical inspection snapshot should be cache hit"}
    if str(first.get("snapshot_hash", "")) != str(second.get("snapshot_hash", "")):
        return {"status": "fail", "message": "electrical inspection snapshot hash drifted under cache reuse"}

    snapshot = dict(second.get("inspection_snapshot") or {})
    summary_sections = dict(snapshot.get("summary_sections") or {})
    if "section.elec.local_panel_state" not in summary_sections:
        return {"status": "fail", "message": "electrical snapshot missing section.elec.local_panel_state"}
    if "section.elec.fault_summary" not in summary_sections:
        return {"status": "fail", "message": "electrical snapshot missing section.elec.fault_summary"}
    return {"status": "pass", "message": "electrical inspection snapshot cache determinism passed"}

