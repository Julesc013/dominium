"""STRICT test: negotiation kernel must be deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_negotiation_deterministic_same_inputs"
TEST_TAGS = ["strict", "control", "negotiation", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.negotiation import negotiate_request
    from tools.xstack.compatx.canonical_json import canonical_sha256

    negotiation_request = {
        "schema_version": "1.0.0",
        "requester_subject_id": "agent.alpha",
        "control_intent_id": "control.intent.alpha",
        "request_vector": {
            "abstraction_level_requested": "AL3",
            "fidelity_requested": "micro",
            "view_requested": "view.mode.first_person",
            "epistemic_scope_requested": "ep.scope.standard",
            "budget_requested": 5,
        },
        "context": {
            "law_profile_id": "law.test",
            "server_profile_id": "server.profile.private",
        },
        "extensions": {
            "required_entitlements": ["entitlement.control.admin"],
            "fidelity_cost_by_level": {"micro": 5, "meso": 3, "macro": 1},
        },
    }
    rs5_state = {
        "tick": 42,
        "max_cost_units_per_tick": 8,
        "runtime_budget_state": {},
        "fairness_state": {},
        "connected_subject_ids": ["agent.alpha"],
    }
    control_policy = {
        "control_policy_id": "ctrl.policy.scheduler",
        "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3"],
        "allowed_view_policies": ["view.mode.first_person"],
        "allowed_fidelity_ranges": ["macro", "meso", "micro"],
        "extensions": {},
    }
    authority_context = {"entitlements": ["entitlement.control.admin"]}

    first = negotiate_request(
        negotiation_request=copy.deepcopy(negotiation_request),
        rs5_budget_state=copy.deepcopy(rs5_state),
        control_policy=copy.deepcopy(control_policy),
        view_policy={"allowed_view_policies": ["view.mode.first_person"]},
        epistemic_policy={"allowed_scope_ids": ["ep.scope.standard"]},
        server_profile={"server_profile_id": "server.profile.private"},
        authority_context=copy.deepcopy(authority_context),
        law_profile={"allowed_processes": [], "forbidden_processes": []},
    )
    second = negotiate_request(
        negotiation_request=copy.deepcopy(negotiation_request),
        rs5_budget_state=copy.deepcopy(rs5_state),
        control_policy=copy.deepcopy(control_policy),
        view_policy={"allowed_view_policies": ["view.mode.first_person"]},
        epistemic_policy={"allowed_scope_ids": ["ep.scope.standard"]},
        server_profile={"server_profile_id": "server.profile.private"},
        authority_context=copy.deepcopy(authority_context),
        law_profile={"allowed_processes": [], "forbidden_processes": []},
    )
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "negotiation kernel output drifted for identical inputs"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "negotiation deterministic_fingerprint mismatch for identical inputs"}
    return {"status": "pass", "message": "negotiation kernel deterministic output check passed"}

