"""STRICT test: Observation Kernel must be deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.observation.determinism"
TEST_TAGS = ["strict", "session", "observation"]


def _truth_fixture():
    return {
        "schema_version": "1.0.0",
        "universe_identity_ref": "saves/save.test/universe_identity.json",
        "universe_state_ref": "saves/save.test/universe_state.json",
        "registry_refs": {
            "domain_registry_hash": "h_domain",
            "law_registry_hash": "h_law",
            "experience_registry_hash": "h_experience",
            "lens_registry_hash": "h_lens",
            "astronomy_catalog_index_hash": "h_catalog",
            "ui_registry_hash": "h_ui",
        },
        "universe_identity": {},
        "universe_state": {
            "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
            "agent_states": [
                {"entity_id": "entity.alpha"},
                {"entity_id": "entity.beta"},
            ],
        },
        "simulation_tick": 0,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = _truth_fixture()
    lens = {
        "lens_id": "lens.test.sensor",
        "lens_type": "diegetic",
        "required_entitlements": ["session.boot"],
        "epistemic_constraints": {"visibility_policy": "sensor_limited", "max_resolution_tier": 1},
    }
    law = {
        "law_profile_id": "law.test.default",
        "allowed_lenses": ["lens.test.sensor"],
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

    first = observe_truth(truth, lens, law, authority, "viewpoint.client.test")
    second = observe_truth(truth, lens, law, authority, "viewpoint.client.test")
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "observation unexpectedly refused for deterministic fixture"}
    if str(first.get("perceived_model_hash", "")) != str(second.get("perceived_model_hash", "")):
        return {"status": "fail", "message": "perceived model hash mismatch across identical observation inputs"}
    if dict(first.get("perceived_model") or {}) != dict(second.get("perceived_model") or {}):
        return {"status": "fail", "message": "perceived model payload mismatch across identical observation inputs"}
    return {"status": "pass", "message": "observation determinism check passed"}
