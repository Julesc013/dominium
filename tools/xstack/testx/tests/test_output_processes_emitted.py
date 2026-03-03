"""FAST test: model outputs emit process-backed mutations."""

from __future__ import annotations

import sys


TEST_ID = "test_output_processes_emitted"
TEST_TAGS = ["fast", "meta", "model", "process"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.model.test",
        "allowed_processes": ["process.model_evaluate_tick"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {"process.model_evaluate_tick": "session.boot"},
        "process_privilege_requirements": {"process.model_evaluate_tick": "observer"},
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "server",
        "subject_id": "subject.server",
        "agent_id": "",
        "entitlements": ["session.boot", "entitlement.inspect"],
        "privilege_level": "observer",
    }


def _policy_context() -> dict:
    return {
        "model_type_registry": {
            "model_types": [
                {
                    "schema_version": "1.0.0",
                    "model_type_id": "model_type.signal_attenuation_stub",
                    "description": "stub",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                }
            ]
        },
        "model_cache_policy_registry": {
            "cache_policies": [
                {"schema_version": "1.0.0", "cache_policy_id": "cache.none", "mode": "none", "ttl_ticks": None, "extensions": {}}
            ]
        },
        "constitutive_model_registry": {
            "models": [
                {
                    "schema_version": "1.0.0",
                    "model_id": "model.runtime.stub",
                    "model_type_id": "model_type.signal_attenuation_stub",
                    "description": "runtime",
                    "supported_tiers": ["macro"],
                    "input_signature": [
                        {"schema_version": "1.0.0", "input_kind": "derived", "input_id": "derived.runtime", "selector": None, "extensions": {}}
                    ],
                    "output_signature": [
                        {"schema_version": "1.0.0", "output_kind": "effect", "output_id": "effect.visibility_reduction", "extensions": {}},
                        {"schema_version": "1.0.0", "output_kind": "hazard_increment", "output_id": "hazard.model.runtime", "extensions": {}},
                        {"schema_version": "1.0.0", "output_kind": "flow_adjustment", "output_id": "quantity.capacity_per_tick", "extensions": {}},
                    ],
                    "cost_units": 1,
                    "cache_policy_id": "cache.none",
                    "uses_rng_stream": False,
                    "rng_stream_name": None,
                    "version_introduced": "1.0.0",
                    "deprecated": False,
                    "deterministic_fingerprint": "",
                    "extensions": {},
                }
            ]
        },
        "field_type_registry": {"field_types": []},
        "field_update_policy_registry": {"policies": []},
    }


def _state() -> dict:
    return {
        "simulation_time": {"schema_version": "1.0.0", "tick": 0, "sim_time_us": 0},
        "model_bindings": [
            {
                "schema_version": "1.0.0",
                "binding_id": "binding.runtime.1",
                "model_id": "model.runtime.stub",
                "target_kind": "channel",
                "target_id": "channel.alpha",
                "tier": "macro",
                "parameters": {},
                "enabled": True,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "signal_channel_rows": [
            {
                "schema_version": "1.0.0",
                "channel_id": "channel.alpha",
                "channel_type_id": "channel.wired_basic",
                "network_graph_id": "graph.signal.alpha",
                "capacity_per_tick": 10,
                "base_delay_ticks": 1,
                "loss_policy_id": "loss.none",
                "encryption_policy_id": None,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "effect_rows": [],
        "effect_provenance_events": [],
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = _state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.model.runtime.1",
            "process_id": "process.model_evaluate_tick",
            "inputs": {"derived_inputs": {"derived.runtime": 1}, "max_cost_units": 8},
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        policy_context=_policy_context(),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "model_evaluate_tick refused: {}".format(result)}
    if int(result.get("output_process_count", 0)) < 3:
        return {"status": "fail", "message": "expected at least 3 output process emissions"}
    if not list(state.get("model_hazard_rows") or []):
        return {"status": "fail", "message": "hazard increment output did not persist"}
    if not list(state.get("model_flow_adjustment_rows") or []):
        return {"status": "fail", "message": "flow adjustment output did not persist"}
    if not list(state.get("effect_rows") or []):
        return {"status": "fail", "message": "effect output did not persist"}
    if not list(state.get("info_artifact_rows") or []):
        return {"status": "fail", "message": "observation artifacts were not emitted"}
    return {"status": "pass", "message": "model outputs emitted process-backed mutations"}

