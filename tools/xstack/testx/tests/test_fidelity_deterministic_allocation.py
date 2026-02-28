"""STRICT test: CTRL-5 fidelity arbitration is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_fidelity_deterministic_allocation"
TEST_TAGS = ["strict", "control", "fidelity", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.fidelity import arbitrate_fidelity_requests, build_fidelity_request
    from tools.xstack.compatx.canonical_json import canonical_sha256

    requests = [
        build_fidelity_request(
            requester_subject_id="subject.alpha",
            target_kind="structure",
            target_id="assembly.structure_instance.alpha",
            requested_level="micro",
            cost_estimate=8,
            priority=2,
            created_tick=10,
            extensions={
                "allowed_levels": ["micro", "meso", "macro"],
                "fidelity_cost_by_level": {"micro": 8, "meso": 5, "macro": 2},
            },
        ),
        build_fidelity_request(
            requester_subject_id="subject.beta",
            target_kind="region",
            target_id="region.beta",
            requested_level="meso",
            cost_estimate=4,
            priority=1,
            created_tick=10,
            extensions={
                "allowed_levels": ["micro", "meso", "macro"],
                "fidelity_cost_by_level": {"micro": 7, "meso": 4, "macro": 2},
            },
        ),
    ]
    rs5_budget_state = {
        "tick": 10,
        "envelope_id": "budget.test",
        "fidelity_policy_id": "fidelity.policy.default",
        "max_cost_units_per_tick": 12,
        "runtime_budget_state": {},
        "fairness_state": {},
        "connected_subject_ids": ["subject.alpha", "subject.beta"],
    }

    first = arbitrate_fidelity_requests(
        fidelity_requests=copy.deepcopy(requests),
        rs5_budget_state=copy.deepcopy(rs5_budget_state),
        server_profile={"server_profile_id": "server.profile.private"},
        fidelity_policy={"policy_id": "fidelity.policy.default"},
    )
    second = arbitrate_fidelity_requests(
        fidelity_requests=copy.deepcopy(requests),
        rs5_budget_state=copy.deepcopy(rs5_budget_state),
        server_profile={"server_profile_id": "server.profile.private"},
        fidelity_policy={"policy_id": "fidelity.policy.default"},
    )

    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "fidelity arbitration output drifted for identical inputs"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "fidelity arbitration fingerprint drifted for identical inputs"}
    return {"status": "pass", "message": "fidelity deterministic allocation check passed"}

