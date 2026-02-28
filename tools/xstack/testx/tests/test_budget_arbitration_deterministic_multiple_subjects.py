"""STRICT test: multi-subject budget arbitration is deterministic across request ordering."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_budget_arbitration_deterministic_multiple_subjects"
TEST_TAGS = ["strict", "control", "negotiation", "budget", "multiplayer"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.negotiation import arbitrate_negotiation_requests
    from tools.xstack.compatx.canonical_json import canonical_sha256

    requests = [
        {
            "schema_version": "1.0.0",
            "requester_subject_id": "subject.beta",
            "control_intent_id": "control.intent.beta.001",
            "request_vector": {
                "abstraction_level_requested": "AL1",
                "fidelity_requested": "meso",
                "view_requested": "view.mode.first_person",
                "epistemic_scope_requested": "ep.scope.standard",
                "budget_requested": 4,
            },
            "context": {"law_profile_id": "law.test", "server_profile_id": "server.profile.private"},
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "requester_subject_id": "subject.alpha",
            "control_intent_id": "control.intent.alpha.001",
            "request_vector": {
                "abstraction_level_requested": "AL1",
                "fidelity_requested": "meso",
                "view_requested": "view.mode.first_person",
                "epistemic_scope_requested": "ep.scope.standard",
                "budget_requested": 4,
            },
            "context": {"law_profile_id": "law.test", "server_profile_id": "server.profile.private"},
            "extensions": {},
        },
    ]
    rs5_budget_state = {
        "tick": 9,
        "max_cost_units_per_tick": 6,
        "runtime_budget_state": {},
        "fairness_state": {},
        "connected_subject_ids": ["subject.alpha", "subject.beta"],
    }
    control_policy = {
        "control_policy_id": "ctrl.policy.scheduler",
        "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
        "allowed_view_policies": ["view.mode.first_person"],
        "allowed_fidelity_ranges": ["macro", "meso", "micro"],
        "extensions": {},
    }

    first = arbitrate_negotiation_requests(
        negotiation_requests=copy.deepcopy(requests),
        rs5_budget_state=copy.deepcopy(rs5_budget_state),
        control_policy=copy.deepcopy(control_policy),
        view_policy={"allowed_view_policies": ["view.mode.first_person"]},
        epistemic_policy={"allowed_scope_ids": ["ep.scope.standard"]},
        server_profile={"server_profile_id": "server.profile.private"},
        authority_context={},
        law_profile={"allowed_processes": [], "forbidden_processes": []},
    )
    second = arbitrate_negotiation_requests(
        negotiation_requests=list(reversed(copy.deepcopy(requests))),
        rs5_budget_state=copy.deepcopy(rs5_budget_state),
        control_policy=copy.deepcopy(control_policy),
        view_policy={"allowed_view_policies": ["view.mode.first_person"]},
        epistemic_policy={"allowed_scope_ids": ["ep.scope.standard"]},
        server_profile={"server_profile_id": "server.profile.private"},
        authority_context={},
        law_profile={"allowed_processes": [], "forbidden_processes": []},
    )
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "budget arbitration output drifted across request-order variation"}
    ordered_keys = list(first.get("ordered_request_keys") or [])
    if ordered_keys != ["subject.alpha::control.intent.alpha.001", "subject.beta::control.intent.beta.001"]:
        return {"status": "fail", "message": "budget arbitration request ordering is not canonical"}
    results = [dict(row) for row in list(first.get("results") or []) if isinstance(row, dict)]
    if len(results) != 2:
        return {"status": "fail", "message": "expected two arbitration results"}
    for row in results:
        allocated = int(max(0, int((dict(row.get("resolved_vector") or {})).get("budget_allocated", 0))))
        if allocated != 3:
            return {"status": "fail", "message": "unexpected fair-share budget allocation in arbitration result"}
    return {"status": "pass", "message": "multi-subject budget arbitration determinism check passed"}

