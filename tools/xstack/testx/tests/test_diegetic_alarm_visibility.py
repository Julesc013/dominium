"""FAST test: CTRL-8 diegetic warnings are coarse while admin sees full effect vectors."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.control.effects.diegetic_alarm_visibility"
TEST_TAGS = ["fast", "control", "effects", "diegetic", "epistemic"]


def _truth_model() -> dict:
    return {
        "universe_state": {
            "simulation_time": {"tick": 42},
            "camera_assemblies": [
                {
                    "assembly_id": "camera.main",
                    "frame_id": "frame.world",
                    "position_mm": {"x": 0, "y": 0, "z": 1200},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "lens_id": "lens.diegetic.effects",
                }
            ],
            "instrument_assemblies": [
                {
                    "assembly_id": "instrument.warning.low_visibility",
                    "instrument_type": "warning.low_visibility",
                    "instrument_type_id": "instr.warning.low_visibility",
                    "reading": {"status": "WARN", "visibility_band": "LOW", "tick": 42},
                    "quality": "coarse",
                    "quality_value": 600,
                    "last_update_tick": 42,
                    "state": {"status": "WARN"},
                    "outputs": {"ch.diegetic.warning.low_visibility": {"status": "WARN", "visibility_band": "LOW", "tick": 42}},
                },
                {
                    "assembly_id": "instrument.warning.restricted_access",
                    "instrument_type": "warning.restricted_access",
                    "instrument_type_id": "instr.warning.restricted_access",
                    "reading": {"status": "WARN", "restricted_access": True, "tick": 42},
                    "quality": "coarse",
                    "quality_value": 600,
                    "last_update_tick": 42,
                    "state": {"status": "WARN"},
                    "outputs": {"ch.diegetic.warning.restricted_access": {"status": "WARN", "restricted_access": True, "tick": 42}},
                },
            ],
            "effect_rows": [
                {
                    "schema_version": "1.0.0",
                    "effect_id": "effect.instance.visibility.alpha",
                    "effect_type_id": "effect.visibility_reduction",
                    "target_id": "portal.ab",
                    "applied_tick": 40,
                    "expires_tick": 100,
                    "duration_ticks": 60,
                    "magnitude": {"visibility_permille": 350},
                    "stacking_policy_id": "stack.min",
                    "source_event_id": "event.effect.demo",
                    "deterministic_fingerprint": "a" * 64,
                    "extensions": {},
                }
            ],
        }
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.observation import observe_truth

    truth = _truth_model()
    retention_policy = {
        "retention_policy_id": "ep.retention.none",
        "memory_allowed": False,
        "max_memory_items": 0,
        "decay_model_id": "none",
        "deterministic_eviction_rule_id": "evict.none",
        "extensions": {},
    }

    diegetic_result = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens={
            "lens_id": "lens.diegetic.effects",
            "lens_type": "diegetic",
            "required_entitlements": ["session.boot"],
            "observation_channels": [
                "ch.core.time",
                "ch.camera.state",
                "ch.diegetic.warning.low_visibility",
                "ch.diegetic.warning.restricted_access",
            ],
            "epistemic_constraints": {"visibility_policy": "sensor_limited"},
        },
        law_profile={
            "law_profile_id": "law.test.effects.diegetic",
            "allowed_lenses": ["lens.diegetic.effects"],
            "epistemic_limits": {"allow_hidden_state_access": False},
        },
        authority_context={
            "authority_origin": "client",
            "experience_id": "profile.test.player",
            "law_profile_id": "law.test.effects.diegetic",
            "entitlements": ["session.boot"],
            "epistemic_scope": {"scope_id": "scope.player", "visibility_level": "diegetic"},
            "privilege_level": "observer",
        },
        viewpoint_id="view.player",
        epistemic_policy={
            "epistemic_policy_id": "ep.policy.player_diegetic",
            "allowed_observation_channels": [
                "ch.core.time",
                "ch.camera.state",
                "ch.diegetic.warning.low_visibility",
                "ch.diegetic.warning.restricted_access",
            ],
            "forbidden_channels": [],
            "retention_policy_id": "ep.retention.none",
            "inference_policy_id": "ep.infer.none",
            "max_precision_rules": [],
            "deterministic_filters": ["filter.channel_allow_deny.v1"],
            "extensions": {},
        },
        retention_policy=copy.deepcopy(retention_policy),
    )
    if str(diegetic_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "diegetic observation unexpectedly refused"}
    diegetic_model = dict(diegetic_result.get("perceived_model") or {})
    diegetic_instruments = dict(diegetic_model.get("diegetic_instruments") or {})
    low_visibility = dict(diegetic_instruments.get("instrument.warning.low_visibility") or {})
    reading = dict(low_visibility.get("reading") or {})
    if str(reading.get("status", "")) != "WARN":
        return {"status": "fail", "message": "diegetic warning channel missing expected WARN status"}
    if "visibility_permille" in reading:
        return {"status": "fail", "message": "diegetic warning leaked hidden numeric visibility value"}
    diegetic_control = dict(diegetic_model.get("control") or {})
    if list(diegetic_control.get("effects") or []):
        return {"status": "fail", "message": "diegetic model must not expose full effect vectors"}

    admin_result = observe_truth(
        truth_model=copy.deepcopy(truth),
        lens={
            "lens_id": "lens.admin.effects",
            "lens_type": "nondiegetic",
            "required_entitlements": ["session.boot"],
            "observation_channels": [
                "ch.core.time",
                "ch.camera.state",
                "ch.core.entities",
                "ch.nondiegetic.entity_inspector",
            ],
            "epistemic_constraints": {"visibility_policy": "lab_full"},
        },
        law_profile={
            "law_profile_id": "law.test.effects.admin",
            "allowed_lenses": ["lens.admin.effects"],
            "epistemic_limits": {"allow_hidden_state_access": True},
        },
        authority_context={
            "authority_origin": "tool",
            "experience_id": "profile.test.admin",
            "law_profile_id": "law.test.effects.admin",
            "entitlements": ["session.boot", "lens.nondiegetic.access", "entitlement.inspect"],
            "epistemic_scope": {"scope_id": "scope.admin", "visibility_level": "lab"},
            "privilege_level": "admin",
        },
        viewpoint_id="view.admin",
        epistemic_policy={
            "epistemic_policy_id": "ep.policy.admin_full",
            "allowed_observation_channels": [
                "ch.core.time",
                "ch.camera.state",
                "ch.core.entities",
                "ch.nondiegetic.entity_inspector",
            ],
            "forbidden_channels": [],
            "retention_policy_id": "ep.retention.none",
            "inference_policy_id": "ep.infer.none",
            "max_precision_rules": [],
            "deterministic_filters": ["filter.channel_allow_deny.v1"],
            "extensions": {},
        },
        retention_policy=copy.deepcopy(retention_policy),
    )
    if str(admin_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "admin observation unexpectedly refused"}
    admin_model = dict(admin_result.get("perceived_model") or {})
    admin_control = dict(admin_model.get("control") or {})
    effect_rows = [dict(row) for row in list(admin_control.get("effects") or []) if isinstance(row, dict)]
    if not effect_rows:
        return {"status": "fail", "message": "admin observation missing full effect vectors"}
    first = dict(effect_rows[0])
    magnitude = dict(first.get("magnitude") or {})
    if int(magnitude.get("visibility_permille", 0) or 0) != 350:
        return {"status": "fail", "message": "admin effect vector magnitude mismatch"}
    return {"status": "pass", "message": "diegetic warnings are coarse while admin sees full effect vectors"}
