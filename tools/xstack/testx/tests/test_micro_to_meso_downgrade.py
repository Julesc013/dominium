"""STRICT test: micro fidelity deterministically downgrades to meso under budget pressure."""

from __future__ import annotations

import sys


TEST_ID = "test_micro_to_meso_downgrade"
TEST_TAGS = ["strict", "control", "fidelity", "downgrade"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.fidelity import DOWNGRADE_BUDGET, arbitrate_fidelity_requests, build_fidelity_request

    request = build_fidelity_request(
        requester_subject_id="subject.gamma",
        target_kind="structure",
        target_id="assembly.structure_instance.gamma",
        requested_level="micro",
        cost_estimate=10,
        priority=0,
        created_tick=3,
        extensions={
            "allowed_levels": ["micro", "meso", "macro"],
            "fidelity_cost_by_level": {"micro": 10, "meso": 6, "macro": 2},
        },
    )
    result = arbitrate_fidelity_requests(
        fidelity_requests=[request],
        rs5_budget_state={
            "tick": 3,
            "envelope_id": "budget.micro_to_meso",
            "fidelity_policy_id": "fidelity.policy.default",
            "max_cost_units_per_tick": 6,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["subject.gamma"],
        },
        server_profile={"server_profile_id": "server.profile.private"},
        fidelity_policy={"policy_id": "fidelity.policy.default"},
    )
    allocations = [dict(row) for row in list(result.get("fidelity_allocations") or []) if isinstance(row, dict)]
    if not allocations:
        return {"status": "fail", "message": "missing fidelity allocation row"}
    allocation = allocations[0]
    if str(allocation.get("resolved_level", "")).strip() != "meso":
        return {"status": "fail", "message": "expected micro request to downgrade to meso"}
    if str(allocation.get("downgrade_reason", "")).strip() != DOWNGRADE_BUDGET:
        return {"status": "fail", "message": "expected downgrade reason to be budget_insufficient"}
    refusal_codes = list((dict(allocation.get("extensions") or {})).get("refusal_codes") or [])
    if refusal_codes:
        return {"status": "fail", "message": "meso downgrade should not emit refusal codes"}
    return {"status": "pass", "message": "micro->meso downgrade check passed"}

