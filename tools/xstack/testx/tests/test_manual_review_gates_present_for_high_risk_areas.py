"""FAST test: PI-1 manual review gates cover the required high-risk areas."""

from __future__ import annotations


TEST_ID = "test_manual_review_gates_present_for_high_risk_areas"
TEST_TAGS = ["fast", "pi", "blueprint", "review"]


def run(repo_root: str):
    from tools.xstack.testx.tests.series_execution_strategy_testlib import committed_manual_review_gates

    payload = committed_manual_review_gates(repo_root)
    gates = list(payload.get("gates") or [])
    gate_ids = {str(dict(row).get("gate_id", "")).strip() for row in gates}
    required = {
        "architecture_graph_changes",
        "semantic_contract_changes",
        "lifecycle_manager_semantics",
        "module_abi_boundaries",
        "trust_root_governance_changes",
        "licensing_commercialization_policy",
        "distributed_authority_model_changes",
        "runtime_privilege_escalation_policies",
        "restartless_core_replacement_mechanisms",
    }
    missing = sorted(required - gate_ids)
    if missing:
        return {"status": "fail", "message": f"missing manual review gates: {', '.join(missing)}"}
    for row in gates:
        current = dict(row)
        if not str(current.get("required_xstack_profile", "")).strip():
            return {"status": "fail", "message": "manual review gates must declare required_xstack_profile"}
    return {"status": "pass", "message": "PI-1 manual review gates cover the required high-risk areas"}
