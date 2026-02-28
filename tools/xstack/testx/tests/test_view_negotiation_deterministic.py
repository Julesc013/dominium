"""STRICT test: view negotiation is deterministic for identical ranked requests."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_view_negotiation_deterministic"
TEST_TAGS = ["strict", "control", "view", "negotiation", "determinism"]


def _request() -> dict:
    return {
        "schema_version": "1.0.0",
        "requester_subject_id": "agent.alpha",
        "control_intent_id": "control.intent.view.det.001",
        "request_vector": {
            "abstraction_level_requested": "AL1",
            "fidelity_requested": "meso",
            "view_requested": "view.freecam_lab",
            "epistemic_scope_requested": "epistemic.admin_full",
        },
        "context": {
            "law_profile_id": "law.test.view.det",
            "server_profile_id": "server.profile.rank_strict",
        },
        "extensions": {
            "required_entitlements": ["entitlement.control.camera"],
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.negotiation import negotiate_request
    from tools.xstack.compatx.canonical_json import canonical_sha256

    request = _request()
    rs5_state = {"tick": 12, "max_cost_units_per_tick": 100, "runtime_budget_state": {}, "fairness_state": {}}
    control_policy = {
        "control_policy_id": "ctrl.policy.player.ranked",
        "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
        "allowed_view_policies": [
            "view.freecam_lab",
            "view.third_person_diegetic",
            "view.first_person_diegetic",
        ],
        "allowed_fidelity_ranges": ["macro", "meso"],
    }
    authority = {"entitlements": ["entitlement.control.camera"]}

    first = negotiate_request(
        negotiation_request=copy.deepcopy(request),
        rs5_budget_state=copy.deepcopy(rs5_state),
        control_policy=copy.deepcopy(control_policy),
        view_policy={"allowed_view_policies": copy.deepcopy(control_policy["allowed_view_policies"])},
        epistemic_policy={"allowed_scope_ids": ["epistemic.admin_full"]},
        server_profile={"server_profile_id": "server.profile.rank_strict"},
        authority_context=copy.deepcopy(authority),
        law_profile={"allowed_processes": ["process.view_bind"], "forbidden_processes": []},
    )
    second = negotiate_request(
        negotiation_request=copy.deepcopy(request),
        rs5_budget_state=copy.deepcopy(rs5_state),
        control_policy=copy.deepcopy(control_policy),
        view_policy={"allowed_view_policies": copy.deepcopy(control_policy["allowed_view_policies"])},
        epistemic_policy={"allowed_scope_ids": ["epistemic.admin_full"]},
        server_profile={"server_profile_id": "server.profile.rank_strict"},
        authority_context=copy.deepcopy(authority),
        law_profile={"allowed_processes": ["process.view_bind"], "forbidden_processes": []},
    )
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "view negotiation output drifted for identical ranked request"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "view negotiation deterministic fingerprint mismatch"}

    resolved = dict(first.get("resolved_vector") or {})
    view_resolved = str(resolved.get("view_resolved", "")).strip()
    if not view_resolved or "freecam" in view_resolved.lower():
        return {"status": "fail", "message": "ranked negotiation must not resolve freecam view"}

    downgrade_rows = [dict(row) for row in list(first.get("downgrade_entries") or []) if isinstance(row, dict)]
    rank_downgrade = [
        row
        for row in downgrade_rows
        if str(row.get("axis", "")).strip() == "view" and str(row.get("reason_code", "")).strip() == "downgrade.rank_fairness"
    ]
    if not rank_downgrade:
        return {"status": "fail", "message": "ranked view negotiation should record downgrade.rank_fairness"}
    return {"status": "pass", "message": "view negotiation determinism check passed"}

