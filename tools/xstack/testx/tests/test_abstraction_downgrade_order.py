"""STRICT test: downgrade entries must follow canonical axis ordering."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_abstraction_downgrade_order"
TEST_TAGS = ["strict", "control", "negotiation", "ordering"]


_AXIS_RANK = {
    "abstraction": 0,
    "view": 1,
    "epistemic": 2,
    "fidelity": 3,
    "budget": 4,
}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.negotiation import negotiate_request

    request = {
        "schema_version": "1.0.0",
        "requester_subject_id": "agent.ordering",
        "control_intent_id": "control.intent.ordering",
        "request_vector": {
            "abstraction_level_requested": "AL4",
            "fidelity_requested": "micro",
            "view_requested": "view.mode.freecam",
            "epistemic_scope_requested": "ep.scope.deep",
            "budget_requested": 5,
        },
        "context": {
            "law_profile_id": "law.test",
            "server_profile_id": "server.profile.ranked.strict",
        },
        "extensions": {
            "fidelity_cost_by_level": {"micro": 5, "meso": 3},
        },
    }
    result = negotiate_request(
        negotiation_request=copy.deepcopy(request),
        rs5_budget_state={
            "tick": 7,
            "max_cost_units_per_tick": 2,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["agent.ordering"],
        },
        control_policy={
            "control_policy_id": "ctrl.policy.test",
            "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
            "allowed_view_policies": ["view.mode.first_person"],
            "allowed_fidelity_ranges": ["macro", "meso", "micro"],
            "extensions": {},
        },
        view_policy={"allowed_view_policies": ["view.mode.first_person"]},
        epistemic_policy={"allowed_scope_ids": ["ep.scope.surface"]},
        server_profile={"server_profile_id": "server.profile.ranked.strict"},
        authority_context={"entitlements": []},
        law_profile={"allowed_processes": [], "forbidden_processes": []},
    )
    downgrade_entries = [dict(row) for row in list(result.get("downgrade_entries") or []) if isinstance(row, dict)]
    if not downgrade_entries:
        return {"status": "fail", "message": "expected downgrade entries missing for ordering test"}
    axes = [str(row.get("axis", "")).strip() for row in downgrade_entries]
    if axes[0] != "abstraction":
        return {"status": "fail", "message": "first downgrade axis must be abstraction"}
    previous_rank = -1
    for axis in axes:
        rank = int(_AXIS_RANK.get(axis, 999))
        if rank < previous_rank:
            return {"status": "fail", "message": "downgrade axis ordering is non-canonical"}
        previous_rank = rank
    return {"status": "pass", "message": "downgrade axis ordering is canonical"}
