"""FAST test: process.weld_joint increases deterministic structural edge strength."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mechanics.weld_increases_strength"
TEST_TAGS = ["fast", "mechanics", "act"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mechanics_testlib import authority_context, base_state, law_profile, policy_context

    state = base_state()
    intent = {
        "intent_id": "intent.mech.weld.001",
        "process_id": "process.weld_joint",
        "inputs": {
            "structural_edge_id": "structural.edge.ab",
            "weld_gain_permille": 1250,
        },
    }
    law = law_profile(["process.weld_joint"])
    authority = authority_context(["entitlement.tool.use"], privilege_level="operator")
    policy = policy_context()
    result = execute_intent(
        state=state,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.weld_joint refused unexpectedly"}
    edge_rows = [dict(row) for row in list(state.get("structural_edges") or []) if isinstance(row, dict)]
    edge = dict(edge_rows[0] if edge_rows else {})
    if int(edge.get("max_load", 0)) <= 1000:
        return {"status": "fail", "message": "weld_joint did not increase max_load"}
    return {"status": "pass", "message": "weld increases structural edge max_load"}

