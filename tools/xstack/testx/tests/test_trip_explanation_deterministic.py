"""FAST test: ELEC-4 trip explanation artifacts are deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_trip_explanation_deterministic"
TEST_TAGS = ["fast", "electric", "inspection", "determinism"]


def _run_fixture(repo_root: str, *, run_suffix: str) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context,
        base_state,
        build_power_graph,
        law_profile,
        model_binding_rows,
        policy_context,
    )

    state = base_state(current_tick=22)
    state["power_network_graphs"] = [build_power_graph(capacity_rating=60, resistance_proxy=9)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=150, motor_demand_p=110, motor_pf_permille=760)

    law = copy.deepcopy(law_profile(["process.elec.network_tick", "process.elec.explain_trip"]))
    law["process_entitlement_requirements"] = dict(law.get("process_entitlement_requirements") or {})
    law["process_privilege_requirements"] = dict(law.get("process_privilege_requirements") or {})
    law["process_entitlement_requirements"]["process.elec.explain_trip"] = "entitlement.inspect"
    law["process_privilege_requirements"]["process.elec.explain_trip"] = "observer"

    authority = copy.deepcopy(authority_context())
    authority["privilege_level"] = "observer"

    policy = copy.deepcopy(policy_context(e1_enabled=True))
    tick_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.trip.explain.tick.{}".format(run_suffix),
            "process_id": "process.elec.network_tick",
            "inputs": {"graph_id": "graph.elec.main"},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(tick_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "network tick failed in trip explanation fixture"}

    device_rows = sorted(
        [dict(row) for row in list(state.get("elec_protection_devices") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("device_id", "")),
    )
    if not device_rows:
        return {"status": "fail", "message": "fixture did not produce electrical protection devices"}
    device_id = str(device_rows[0].get("device_id", "")).strip()
    if not device_id:
        return {"status": "fail", "message": "fixture produced protection row without deterministic device_id"}

    explain_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec4.trip.explain.generate.{}".format(run_suffix),
            "process_id": "process.elec.explain_trip",
            "inputs": {"device_id": device_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(explain_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.elec.explain_trip failed in deterministic fixture"}
    metadata = dict(explain_result.get("result_metadata") or {})
    explanation = dict(metadata.get("trip_explanation") or {})
    if not explanation:
        return {"status": "fail", "message": "missing trip_explanation payload in process metadata"}

    return {
        "status": "pass",
        "explanation_id": str(metadata.get("explanation_id", "")).strip(),
        "fingerprint": str(explanation.get("deterministic_fingerprint", "")).strip(),
        "trip_explanation_hash_chain": str(state.get("trip_explanation_hash_chain", "")).strip(),
        "metadata_hash_chain": str(metadata.get("trip_explanation_hash_chain", "")).strip(),
        "fault_ids": sorted(str(item).strip() for item in list(explanation.get("fault_ids") or []) if str(item).strip()),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_fixture(repo_root, run_suffix="A")
    if str(first.get("status", "")) != "pass":
        return first
    second = _run_fixture(repo_root, run_suffix="B")
    if str(second.get("status", "")) != "pass":
        return second

    if str(first.get("explanation_id", "")) != str(second.get("explanation_id", "")):
        return {"status": "fail", "message": "trip explanation_id drifted across identical deterministic fixtures"}
    if str(first.get("fingerprint", "")) != str(second.get("fingerprint", "")):
        return {"status": "fail", "message": "trip explanation deterministic_fingerprint drifted"}
    if str(first.get("trip_explanation_hash_chain", "")) != str(second.get("trip_explanation_hash_chain", "")):
        return {"status": "fail", "message": "trip explanation hash chain drifted across deterministic fixtures"}
    if str(first.get("metadata_hash_chain", "")) != str(first.get("trip_explanation_hash_chain", "")):
        return {"status": "fail", "message": "process metadata missing consistent trip_explanation_hash_chain"}
    if list(first.get("fault_ids") or []) != list(second.get("fault_ids") or []):
        return {"status": "fail", "message": "trip explanation fault linkage drifted across deterministic fixtures"}
    return {"status": "pass", "message": "trip explanation artifact generation is deterministic"}

