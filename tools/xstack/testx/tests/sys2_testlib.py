"""Shared SYS-2 macro capsule fixtures/helpers."""

from __future__ import annotations

import copy
import json
import os

from tools.xstack.testx.tests.sys0_testlib import cloned_state as sys0_cloned_state


def _read_registry_payload(*, repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(str(repo_root), str(rel_path).replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    if isinstance(payload.get("record"), dict):
        return dict(payload.get("record") or {})
    return dict(payload)


def law_profile() -> dict:
    return {
        "law_profile_id": "law.sys2.test",
        "allowed_processes": [
            "process.system_macro_tick",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.system_macro_tick": "session.boot",
        },
        "process_privilege_requirements": {
            "process.system_macro_tick": "observer",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys2.test",
        "entitlements": ["session.boot"],
        "privilege_level": "observer",
    }


def macro_model_set_stub_registry() -> dict:
    return {
        "macro_model_sets": [
            {
                "schema_version": "1.0.0",
                "macro_model_set_id": "macro.set.sys2.stub",
                "model_bindings": [
                    {
                        "binding_id": "binding.sys2.stub.pump",
                        "model_id": "model.fluid.pump_curve.default",
                        "input_port_ids": ["port.fuel_in"],
                        "output_port_ids": ["port.power_out"],
                        "extensions": {
                            "output_process_map": {
                                "flow.adjust.pressure_head_delta": "process.flow_adjust"
                            }
                        },
                    }
                ],
                "error_bound_policy_id": "tol.strict",
                "validity_conditions": {},
                "deterministic_fingerprint": "",
                "extensions": {"source": "SYS2-TestX"},
            }
        ]
    }


def macro_model_set_error_registry() -> dict:
    return {
        "macro_model_sets": [
            {
                "schema_version": "1.0.0",
                "macro_model_set_id": "macro.set.sys2.error",
                "model_bindings": [
                    {
                        "binding_id": "binding.sys2.error.loss_a",
                        "model_id": "model.elec_device_loss",
                        "input_port_ids": ["port.fuel_in"],
                        "output_port_ids": ["port.power_out"],
                        "extensions": {},
                    },
                    {
                        "binding_id": "binding.sys2.error.loss_b",
                        "model_id": "model.elec_load_resistive_stub",
                        "input_port_ids": ["port.fuel_in"],
                        "output_port_ids": ["port.power_out"],
                        "extensions": {},
                    },
                ],
                "error_bound_policy_id": "tol.strict",
                "validity_conditions": {},
                "deterministic_fingerprint": "",
                "extensions": {"source": "SYS2-TestX"},
            }
        ]
    }


def base_state(*, macro_model_set_id: str = "macro.set.sys2.stub", max_error_estimate: int = 8) -> dict:
    state = copy.deepcopy(sys0_cloned_state())
    if state.get("system_rows"):
        system_row = dict((state.get("system_rows") or [])[0])
        ext = dict(system_row.get("extensions") or {})
        ext["macro_model_set_id"] = str(macro_model_set_id)
        ext["model_error_bounds_ref"] = "tol.strict"
        system_row["extensions"] = ext
        system_row["current_tier"] = "macro"
        system_row["active_capsule_id"] = "capsule.system.engine.alpha"
        state["system_rows"] = [system_row]

    state["system_macro_capsule_rows"] = [
        {
            "schema_version": "1.1.0",
            "capsule_id": "capsule.system.engine.alpha",
            "system_id": "system.engine.alpha",
            "interface_signature_id": "iface.system.engine.alpha",
            "macro_model_set_id": str(macro_model_set_id),
            "model_error_bounds_ref": "tol.strict",
            "macro_model_bindings": [],
            "internal_state_vector": {"state_vector_id": "statevec.system.engine.alpha"},
            "provenance_anchor_hash": "hash.anchor.sys2.stub",
            "tier_mode": "macro",
            "deterministic_fingerprint": "",
            "extensions": {
                "boundary_inputs": {
                    "port.fuel_in": 900,
                    "port.power_out": 0,
                },
                "flow_channel_by_port": {
                    "port.power_out": "channel.system.sys2.power",
                },
                "hazard_level": 0,
                "forced_expand_hazard_threshold": 10_000,
                "max_error_estimate": int(max(1, int(max_error_estimate))),
                "fail_safe_on_forced_expand": True,
                "region_id": "region.default",
                "default_pollutant_id": "pollutant.smoke_particulate",
            },
        }
    ]
    state["system_macro_runtime_state_rows"] = []
    state["system_forced_expand_event_rows"] = []
    state["system_macro_output_record_rows"] = []
    state["system_macro_effect_apply_rows"] = []
    state["control_decision_log"] = []
    state["signal_channel_rows"] = [
        {
            "schema_version": "1.0.0",
            "channel_id": "channel.system.sys2.power",
            "channel_type_id": "channel.wired_basic",
            "capacity_per_tick": 4096,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    state["signal_channels"] = [dict(row) for row in list(state.get("signal_channel_rows") or [])]
    state["field_cells"] = []
    return state


def policy_context_for_macro(
    *,
    repo_root: str,
    macro_model_set_registry: dict | None = None,
) -> dict:
    return {
        "macro_model_set_registry": dict(macro_model_set_registry or macro_model_set_stub_registry()),
        "constitutive_model_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/constitutive_model_registry.json",
        ),
        "model_type_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/model_type_registry.json",
        ),
        "model_cache_policy_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/model_cache_policy_registry.json",
        ),
        "tolerance_policy_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/tolerance_policy_registry.json",
        ),
        "model_residual_policy_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/model_residual_policy_registry.json",
        ),
        "pollutant_type_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/pollutant_type_registry.json",
        ),
        "explain_contract_registry": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/explain_contract_registry.json",
        ),
        "system_macro_max_capsules_per_tick": 16,
        "system_macro_tick_bucket_stride": 1,
        "system_macro_max_cost_units_per_capsule": 64,
        "system_macro_max_forced_expand_approvals_per_tick": 16,
    }


def execute_macro_tick(
    *,
    state: dict,
    repo_root: str,
    inputs: dict | None = None,
    policy_context: dict | None = None,
) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys2.system_macro_tick.{}".format(
                str((inputs or {}).get("nonce", "default"))
            ),
            "process_id": "process.system_macro_tick",
            "inputs": dict(inputs or {}),
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_context or {}),
    )

