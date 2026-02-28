"""STRICT test: ranked fidelity policy enforces deterministic equal-share baseline allocation."""

from __future__ import annotations

import sys


TEST_ID = "test_ranked_equal_share"
TEST_TAGS = ["strict", "control", "fidelity", "ranked", "fairness"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.fidelity import RANK_FAIR_POLICY_ID, arbitrate_fidelity_requests, build_fidelity_request

    requests = [
        build_fidelity_request(
            requester_subject_id="subject.alpha",
            target_kind="region",
            target_id="region.alpha",
            requested_level="micro",
            cost_estimate=7,
            priority=0,
            created_tick=11,
            extensions={
                "allowed_levels": ["micro", "meso", "macro"],
                "fidelity_cost_by_level": {"micro": 7, "meso": 5, "macro": 1},
            },
        ),
        build_fidelity_request(
            requester_subject_id="subject.beta",
            target_kind="region",
            target_id="region.beta",
            requested_level="micro",
            cost_estimate=7,
            priority=0,
            created_tick=11,
            extensions={
                "allowed_levels": ["micro", "meso", "macro"],
                "fidelity_cost_by_level": {"micro": 7, "meso": 5, "macro": 1},
            },
        ),
    ]
    result = arbitrate_fidelity_requests(
        fidelity_requests=requests,
        rs5_budget_state={
            "tick": 11,
            "envelope_id": "budget.rank",
            "fidelity_policy_id": RANK_FAIR_POLICY_ID,
            "max_cost_units_per_tick": 10,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["subject.alpha", "subject.beta"],
        },
        server_profile={"server_profile_id": "server.profile.rank_strict"},
        fidelity_policy={"policy_id": RANK_FAIR_POLICY_ID},
    )

    records = [dict(row) for row in list(result.get("budget_allocation_records") or []) if isinstance(row, dict)]
    by_subject = dict((str(row.get("subject_id", "")).strip(), row) for row in records if str(row.get("subject_id", "")).strip())
    alpha = int(by_subject.get("subject.alpha", {}).get("total_cost_allocated", 0) or 0)
    beta = int(by_subject.get("subject.beta", {}).get("total_cost_allocated", 0) or 0)
    if alpha != beta:
        return {"status": "fail", "message": "ranked equal-share baseline allocation diverged across subjects"}
    if alpha != 5:
        return {"status": "fail", "message": "expected ranked equal-share baseline of 5 cost units each"}
    if int(result.get("total_cost_allocated", 0) or 0) != 10:
        return {"status": "fail", "message": "ranked equal-share allocation should consume entire 10-unit envelope"}
    return {"status": "pass", "message": "ranked equal-share allocation check passed"}

