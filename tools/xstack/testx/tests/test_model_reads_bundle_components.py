"""FAST test: model evaluation can read bundle component flow inputs deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_model_reads_bundle_components"
TEST_TAGS = ["fast", "meta", "model", "bundle"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.model.bundle",
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
                    "model_id": "model.bundle.reader",
                    "model_type_id": "model_type.signal_attenuation_stub",
                    "description": "bundle reader",
                    "supported_tiers": ["macro"],
                    "input_signature": [
                        {
                            "schema_version": "1.0.0",
                            "input_kind": "flow_quantity",
                            "input_id": "quantity.power.p",
                            "selector": "channel:channel.bundle:component:quantity.power.p",
                            "extensions": {},
                        }
                    ],
                    "output_signature": [
                        {
                            "schema_version": "1.0.0",
                            "output_kind": "derived_quantity",
                            "output_id": "derived.bundle.reader",
                            "extensions": {},
                        }
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
                "binding_id": "binding.bundle.reader",
                "model_id": "model.bundle.reader",
                "target_kind": "channel",
                "target_id": "channel.bundle",
                "tier": "macro",
                "parameters": {
                    "quantity_bundle_id": "bundle.power_phasor",
                    "component_quantity_id": "quantity.power.p",
                },
                "enabled": True,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "signal_channel_rows": [
            {
                "schema_version": "1.0.0",
                "channel_id": "channel.bundle",
                "channel_type_id": "channel.wired_basic",
                "network_graph_id": "graph.signal.bundle",
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


def _run_eval(repo_root: str, *, flow_value: int):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = _state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.model.bundle.1",
            "process_id": "process.model_evaluate_tick",
            "inputs": {
                "flow_quantities": {"channel.bundle::quantity.power.p": int(flow_value)},
                "max_cost_units": 8,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        policy_context=_policy_context(),
    )
    return state, result


def run(repo_root: str):
    state_a, result_a = _run_eval(repo_root, flow_value=11)
    state_b, result_b = _run_eval(repo_root, flow_value=19)
    if str(result_a.get("result", "")) != "complete":
        return {"status": "fail", "message": "first model_evaluate_tick refused: {}".format(result_a)}
    if str(result_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "second model_evaluate_tick refused: {}".format(result_b)}
    rows_a = list(state_a.get("model_evaluation_results") or [])
    rows_b = list(state_b.get("model_evaluation_results") or [])
    if (not rows_a) or (not rows_b):
        return {"status": "fail", "message": "missing model_evaluation_results rows"}
    hash_a = str(dict(rows_a[-1]).get("inputs_hash", ""))
    hash_b = str(dict(rows_b[-1]).get("inputs_hash", ""))
    if hash_a == hash_b:
        return {"status": "fail", "message": "bundle component flow input did not affect inputs_hash"}
    return {"status": "pass", "message": "model bundle component input path active and deterministic"}
