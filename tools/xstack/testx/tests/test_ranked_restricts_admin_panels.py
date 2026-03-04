"""STRICT test: ranked/diegetic electrical inspection hides admin-only panel details."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_ranked_restricts_admin_panels"
TEST_TAGS = ["strict", "electric", "inspection", "epistemic", "ranked"]


def _run_inspection(
    *,
    state: dict,
    law: dict,
    authority: dict,
    policy: dict,
) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.rank.panel.inspect",
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {"target_id": "graph.elec.main", "desired_fidelity": "meso", "max_cost_units": 2},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


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

    base = base_state(current_tick=55)
    base["power_network_graphs"] = [build_power_graph(capacity_rating=260, resistance_proxy=6)]
    base["model_bindings"] = model_binding_rows(resistive_demand_p=130, motor_demand_p=85, motor_pf_permille=880)

    seeded_state = copy.deepcopy(base)
    tick_law = copy.deepcopy(law_profile(["process.elec.network_tick"]))
    tick_auth = copy.deepcopy(authority_context())
    tick_auth["privilege_level"] = "observer"
    tick_policy = copy.deepcopy(policy_context(e1_enabled=True))
    tick_result = execute_intent(
        state=seeded_state,
        intent={
            "intent_id": "intent.elec4.rank.panel.tick",
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(tick_law),
        authority_context=copy.deepcopy(tick_auth),
        navigation_indices={},
        policy_context=copy.deepcopy(tick_policy),
    )
    if str(tick_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed in ranked panel fixture"}

    ranked_state = copy.deepcopy(seeded_state)
    ranked_law = copy.deepcopy(law_profile(["process.inspect_generate_snapshot"]))
    ranked_law["process_entitlement_requirements"] = dict(ranked_law.get("process_entitlement_requirements") or {})
    ranked_law["process_privilege_requirements"] = dict(ranked_law.get("process_privilege_requirements") or {})
    ranked_law["process_entitlement_requirements"]["process.inspect_generate_snapshot"] = "entitlement.inspect"
    ranked_law["process_privilege_requirements"]["process.inspect_generate_snapshot"] = "observer"
    ranked_law["epistemic_limits"] = dict(ranked_law.get("epistemic_limits") or {})
    ranked_law["epistemic_limits"]["allow_hidden_state_access"] = False
    ranked_law["epistemic_policy_id"] = "ep.policy.player_diegetic"

    ranked_auth = copy.deepcopy(authority_context())
    ranked_scope = dict(ranked_auth.get("epistemic_scope") or {})
    ranked_scope["visibility_level"] = "diegetic"
    ranked_auth["epistemic_scope"] = ranked_scope
    ranked_auth["privilege_level"] = "observer"

    ranked_policy = copy.deepcopy(policy_context(e1_enabled=True))
    ranked_result = _run_inspection(state=ranked_state, law=ranked_law, authority=ranked_auth, policy=ranked_policy)
    if str(ranked_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "ranked/diegetic electrical inspection unexpectedly refused"}

    admin_state = copy.deepcopy(seeded_state)
    admin_law = copy.deepcopy(law_profile(["process.inspect_generate_snapshot"]))
    admin_law["process_entitlement_requirements"] = dict(admin_law.get("process_entitlement_requirements") or {})
    admin_law["process_privilege_requirements"] = dict(admin_law.get("process_privilege_requirements") or {})
    admin_law["process_entitlement_requirements"]["process.inspect_generate_snapshot"] = "entitlement.inspect"
    admin_law["process_privilege_requirements"]["process.inspect_generate_snapshot"] = "observer"
    admin_law["epistemic_limits"] = dict(admin_law.get("epistemic_limits") or {})
    admin_law["epistemic_limits"]["allow_hidden_state_access"] = True
    admin_law["epistemic_policy_id"] = "ep.policy.lab_broad"

    admin_auth = copy.deepcopy(authority_context())
    admin_scope = dict(admin_auth.get("epistemic_scope") or {})
    admin_scope["visibility_level"] = "nondiegetic"
    admin_auth["epistemic_scope"] = admin_scope
    admin_auth["privilege_level"] = "observer"

    admin_policy = copy.deepcopy(policy_context(e1_enabled=True))
    admin_result = _run_inspection(state=admin_state, law=admin_law, authority=admin_auth, policy=admin_policy)
    if str(admin_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "admin electrical inspection unexpectedly refused"}

    ranked_snapshot = dict(ranked_result.get("inspection_snapshot") or {})
    admin_snapshot = dict(admin_result.get("inspection_snapshot") or {})
    ranked_sections = dict(ranked_snapshot.get("summary_sections") or {})
    admin_sections = dict(admin_snapshot.get("summary_sections") or {})
    ranked_device_states = dict(ranked_sections.get("section.elec.device_states") or {})
    admin_device_states = dict(admin_sections.get("section.elec.device_states") or {})

    if not ranked_device_states or not admin_device_states:
        return {"status": "fail", "message": "fixture missing section.elec.device_states summary"}
    if "devices" in ranked_device_states or "trip_explanations" in ranked_device_states:
        return {"status": "fail", "message": "ranked/diegetic inspection leaked admin-only device details"}
    if "devices" not in admin_device_states:
        return {"status": "fail", "message": "admin inspection should expose detailed electrical device states"}
    if "trip_explanations" not in admin_device_states:
        return {"status": "fail", "message": "admin inspection should expose trip explanation detail rows"}
    return {"status": "pass", "message": "ranked/diegetic inspection correctly restricts admin electrical panels"}

