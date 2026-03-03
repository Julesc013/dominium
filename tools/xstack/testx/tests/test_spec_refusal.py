"""FAST test: electrical wire connect refuses deterministic spec mismatch."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_spec_refusal"
TEST_TAGS = ["fast", "electric", "spec", "refusal"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context,
        base_state,
        build_power_graph,
        law_profile,
        mismatched_spec_rows,
        policy_context,
    )

    state = base_state(current_tick=3)
    state["power_network_graphs"] = [build_power_graph(with_edge_spec=True)]

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.elec.spec.refusal.connect",
            "process_id": "process.elec.connect_wire",
            "inputs": {
                "graph_id": "graph.elec.main",
                "edge_id": "edge.elec.main",
                "connector_spec_id": "spec.elec.connector.main",
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.elec.connect_wire"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context(spec_sheet_rows=mismatched_spec_rows())),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "expected process refusal for connector/edge spec mismatch"}
    refusal = dict(result.get("refusal") or {})
    if str(refusal.get("reason_code", "")).strip() != "refusal.elec.spec_noncompliant":
        return {"status": "fail", "message": "unexpected refusal code for mismatched electrical specs"}
    return {"status": "pass", "message": "spec mismatch refusal emitted deterministically"}

