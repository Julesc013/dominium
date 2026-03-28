"""STRICT test: ranked fidelity arbitration keeps equal-share allocation."""

from __future__ import annotations

import sys


TEST_ID = "test_equal_fidelity_allocation_ranked"
TEST_TAGS = ["strict", "control", "fidelity", "ranked", "fairness"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.fidelity import RANK_FAIR_POLICY_ID, arbitrate_fidelity_requests, build_fidelity_request

    subject_ids = ["subject.alpha", "subject.beta", "subject.gamma", "subject.delta"]
    requests = [
        build_fidelity_request(
            requester_subject_id=subject_id,
            target_kind="region",
            target_id="region.{}".format(subject_id.split(".")[-1]),
            requested_level="micro",
            cost_estimate=7,
            priority=0,
            created_tick=22,
            extensions={
                "allowed_levels": ["micro", "meso", "macro"],
                "fidelity_cost_by_level": {"micro": 7, "meso": 5, "macro": 1},
            },
        )
        for subject_id in subject_ids
    ]
    result = arbitrate_fidelity_requests(
        fidelity_requests=requests,
        rs5_budget_state={
            "tick": 22,
            "envelope_id": "budget.ctrl9.rank.equal",
            "fidelity_policy_id": RANK_FAIR_POLICY_ID,
            "max_cost_units_per_tick": 20,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": list(subject_ids),
        },
        server_profile={"server_profile_id": "server.profile.ranked.strict"},
        fidelity_policy={"policy_id": RANK_FAIR_POLICY_ID},
    )
    records = [dict(row) for row in list(result.get("budget_allocation_records") or []) if isinstance(row, dict)]
    by_subject = dict((str(row.get("subject_id", "")).strip(), int(row.get("total_cost_allocated", 0) or 0)) for row in records)
    values = [by_subject.get(subject_id, -1) for subject_id in subject_ids]
    if any(value < 0 for value in values):
        return {"status": "fail", "message": "missing ranked allocation record for one or more subjects"}
    if len(set(values)) != 1:
        return {"status": "fail", "message": "ranked equal-share baseline allocation diverged across subjects"}
    if values[0] != 5:
        return {"status": "fail", "message": "ranked equal-share allocation must be 5 units per subject under 20-unit envelope"}
    if int(result.get("total_cost_allocated", 0) or 0) != 20:
        return {"status": "fail", "message": "ranked allocation should consume full envelope deterministically"}
    return {"status": "pass", "message": "ranked equal-share fidelity allocation passed"}

