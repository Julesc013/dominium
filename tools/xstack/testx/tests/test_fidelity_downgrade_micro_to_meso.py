"""STRICT test: fidelity downgrade from micro to meso is deterministic when micro is disallowed."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_fidelity_downgrade_micro_to_meso"
TEST_TAGS = ["strict", "control", "negotiation", "fidelity"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.negotiation import negotiate_request

    result = negotiate_request(
        negotiation_request={
            "schema_version": "1.0.0",
            "requester_subject_id": "agent.fidelity",
            "control_intent_id": "control.intent.fidelity",
            "request_vector": {
                "abstraction_level_requested": "AL1",
                "fidelity_requested": "micro",
                "view_requested": "view.mode.first_person",
                "epistemic_scope_requested": "ep.scope.standard",
                "budget_requested": 3,
            },
            "context": {"law_profile_id": "law.test", "server_profile_id": "server.profile.private"},
            "extensions": {},
        },
        rs5_budget_state={
            "tick": 1,
            "max_cost_units_per_tick": 6,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["agent.fidelity"],
        },
        control_policy={
            "control_policy_id": "ctrl.policy.test",
            "allowed_abstraction_levels": ["AL0", "AL1"],
            "allowed_view_policies": ["view.mode.first_person"],
            "allowed_fidelity_ranges": ["macro", "meso"],
            "extensions": {},
        },
        view_policy={"allowed_view_policies": ["view.mode.first_person"]},
        epistemic_policy={"allowed_scope_ids": ["ep.scope.standard"]},
        server_profile={"server_profile_id": "server.profile.private"},
        authority_context={"entitlements": []},
        law_profile={"allowed_processes": [], "forbidden_processes": []},
    )

    resolved_fidelity = str((dict(result.get("resolved_vector") or {})).get("fidelity_resolved", "")).strip()
    if resolved_fidelity != "meso":
        return {"status": "fail", "message": "expected fidelity to downgrade from micro to meso"}
    downgrade_entries = [dict(row) for row in list(result.get("downgrade_entries") or []) if isinstance(row, dict)]
    fidelity_entries = [row for row in downgrade_entries if str(row.get("axis", "")).strip() == "fidelity"]
    if not fidelity_entries:
        return {"status": "fail", "message": "expected fidelity downgrade entry missing"}
    selected = sorted(
        fidelity_entries,
        key=lambda row: (
            str(row.get("from_value", "")),
            str(row.get("to_value", "")),
            str(row.get("reason_code", "")),
            str(row.get("downgrade_id", "")),
        ),
    )[0]
    if str(selected.get("from_value", "")).strip() != "micro" or str(selected.get("to_value", "")).strip() != "meso":
        return {"status": "fail", "message": "fidelity downgrade entry does not match micro->meso"}
    return {"status": "pass", "message": "fidelity downgrade micro->meso check passed"}

