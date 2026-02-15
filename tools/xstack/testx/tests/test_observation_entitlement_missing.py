"""STRICT test: nondiegetic lens without entitlement must refuse deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.observation.entitlement_missing"
TEST_TAGS = ["strict", "session", "observation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = {
        "universe_state": {
            "simulation_time": {"tick": 0},
            "agent_states": [],
        }
    }
    lens = {
        "lens_id": "lens.test.debug",
        "lens_type": "nondiegetic",
        "required_entitlements": ["ui.debug.overlay"],
        "epistemic_constraints": {"visibility_policy": "admin_debug", "max_resolution_tier": 4},
    }
    law = {
        "law_profile_id": "law.test.default",
        "allowed_lenses": ["lens.test.debug"],
        "epistemic_limits": {"max_view_radius_km": 10000, "allow_hidden_state_access": False},
    }
    authority = {
        "authority_origin": "client",
        "experience_id": "experience.test.lab",
        "law_profile_id": "law.test.default",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "epistemic.test", "visibility_level": "sensor_limited"},
        "privilege_level": "observer",
    }

    result = observe_truth(truth, lens, law, authority, "viewpoint.client.test")
    if result.get("result") != "refused":
        return {"status": "fail", "message": "missing entitlement case must refuse"}
    refusal = result.get("refusal") or {}
    if str(refusal.get("reason_code", "")) != "ENTITLEMENT_MISSING":
        return {"status": "fail", "message": "unexpected refusal reason for missing entitlement"}
    return {"status": "pass", "message": "nondiegetic entitlement refusal check passed"}
