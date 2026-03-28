"""STRICT test: fidelity arbitration never exceeds RS-5 envelope capacity."""

from __future__ import annotations

import sys


TEST_ID = "test_cost_envelope_never_exceeded"
TEST_TAGS = ["strict", "control", "fidelity", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.fidelity import arbitrate_fidelity_requests, build_fidelity_request

    requests = [
        build_fidelity_request(
            requester_subject_id="subject.one",
            target_kind="structure",
            target_id="assembly.structure_instance.one",
            requested_level="micro",
            cost_estimate=9,
            priority=3,
            created_tick=5,
            extensions={"fidelity_cost_by_level": {"micro": 9, "meso": 6, "macro": 2}},
        ),
        build_fidelity_request(
            requester_subject_id="subject.two",
            target_kind="structure",
            target_id="assembly.structure_instance.two",
            requested_level="micro",
            cost_estimate=8,
            priority=2,
            created_tick=5,
            extensions={"fidelity_cost_by_level": {"micro": 8, "meso": 5, "macro": 2}},
        ),
        build_fidelity_request(
            requester_subject_id="subject.three",
            target_kind="structure",
            target_id="assembly.structure_instance.three",
            requested_level="meso",
            cost_estimate=4,
            priority=1,
            created_tick=5,
            extensions={"fidelity_cost_by_level": {"micro": 8, "meso": 4, "macro": 2}},
        ),
    ]
    result = arbitrate_fidelity_requests(
        fidelity_requests=requests,
        rs5_budget_state={
            "tick": 5,
            "envelope_id": "budget.envelope.cap",
            "fidelity_policy_id": "fidelity.policy.default",
            "max_cost_units_per_tick": 9,
            "runtime_budget_state": {"used_by_tick": {"5": 2}},
            "fairness_state": {},
            "connected_subject_ids": ["subject.one", "subject.two", "subject.three"],
        },
        server_profile={"server_profile_id": "server.profile.private"},
        fidelity_policy={"policy_id": "fidelity.policy.default"},
    )

    total_allocated = int(result.get("total_cost_allocated", 0) or 0)
    if total_allocated > 7:
        return {"status": "fail", "message": "allocated fidelity cost exceeded remaining envelope budget (7)"}
    used_after_total = int((dict(result.get("extensions") or {})).get("used_after_total", 0) or 0)
    if used_after_total > 9:
        return {"status": "fail", "message": "used_after_total exceeded envelope max_cost_units_per_tick"}
    runtime_state = dict(result.get("runtime_budget_state") or {})
    used_by_tick = dict(runtime_state.get("used_by_tick") or {})
    if int(used_by_tick.get("5", 0) or 0) > 9:
        return {"status": "fail", "message": "runtime used_by_tick exceeded envelope max for tick 5"}
    return {"status": "pass", "message": "cost envelope bound check passed"}

