"""Shared SYS-3 tier/ROI TestX fixtures/helpers."""

from __future__ import annotations

import copy
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.testx.tests.sys0_testlib import cloned_state as sys0_cloned_state


def law_profile() -> dict:
    return {
        "law_profile_id": "law.sys3.test",
        "allowed_processes": [
            "process.system_roi_tick",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.system_roi_tick": "session.boot",
        },
        "process_privilege_requirements": {
            "process.system_roi_tick": "observer",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys3.test",
        "entitlements": ["session.boot"],
        "privilege_level": "observer",
    }


def _beta_internal_assembly_rows() -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "assembly_id": "assembly.engine.root.beta",
            "assembly_type_id": "assembly.engine.root",
            "deterministic_fingerprint": "",
            "extensions": {"powertrain_role": "root"},
        },
        {
            "schema_version": "1.0.0",
            "assembly_id": "assembly.engine.pump.beta",
            "assembly_type_id": "assembly.pump",
            "deterministic_fingerprint": "",
            "extensions": {"powertrain_role": "pump"},
        },
        {
            "schema_version": "1.0.0",
            "assembly_id": "assembly.engine.generator.beta",
            "assembly_type_id": "assembly.generator",
            "deterministic_fingerprint": "",
            "extensions": {"powertrain_role": "generator"},
        },
    ]


def base_state_two_systems() -> dict:
    state = copy.deepcopy(sys0_cloned_state())

    alpha_system = dict((state.get("system_rows") or [])[0])
    beta_system = copy.deepcopy(alpha_system)
    beta_system.update(
        {
            "system_id": "system.engine.beta",
            "root_assembly_id": "assembly.engine.root.beta",
            "assembly_ids": [
                "assembly.engine.root.beta",
                "assembly.engine.pump.beta",
                "assembly.engine.generator.beta",
            ],
            "interface_signature_id": "iface.system.engine.beta",
            "current_tier": "macro",
            "active_capsule_id": "capsule.system.engine.beta",
        }
    )
    beta_ext = dict(beta_system.get("extensions") or {})
    beta_ext["placeholder_assembly_id"] = "assembly.system_capsule_placeholder.system.engine.beta"
    beta_system["extensions"] = beta_ext
    state["system_rows"] = [alpha_system, beta_system]

    alpha_interface = dict((state.get("system_interface_signature_rows") or [])[0])
    beta_interface = copy.deepcopy(alpha_interface)
    beta_interface.update(
        {
            "system_id": "system.engine.beta",
            "interface_signature_id": "iface.system.engine.beta",
            "signal_channels": [
                {"channel_id": "sig.engine.control.beta", "direction": "bidir"}
            ],
        }
    )
    state["system_interface_signature_rows"] = [alpha_interface, beta_interface]

    beta_internal_state = {
        "schema_version": "1.0.0",
        "encoding": "canonical_json.v1",
        "system_id": "system.engine.beta",
        "captured_tick": 0,
        "assembly_rows": _beta_internal_assembly_rows(),
    }
    beta_anchor_hash = canonical_sha256(beta_internal_state)
    beta_state_vector_id = "statevec.system.{}".format(
        canonical_sha256({"system_id": "system.engine.beta", "tick": 0})[:16]
    )
    state["system_state_vector_rows"] = [
        {
            "schema_version": "1.0.0",
            "state_vector_id": beta_state_vector_id,
            "system_id": "system.engine.beta",
            "serialized_internal_state": beta_internal_state,
            "deterministic_fingerprint": "",
            "extensions": {
                "source_process_id": "process.system_collapse",
                "captured_assembly_count": 3,
                "anchor_hash": beta_anchor_hash,
            },
        }
    ]
    state["system_macro_capsule_rows"] = [
        {
            "schema_version": "1.1.0",
            "capsule_id": "capsule.system.engine.beta",
            "system_id": "system.engine.beta",
            "interface_signature_id": "iface.system.engine.beta",
            "macro_model_set_id": "macro.set.sys2.stub",
            "model_error_bounds_ref": "tol.strict",
            "macro_model_bindings": [],
            "internal_state_vector": {
                "state_vector_id": beta_state_vector_id,
                "anchor_hash": beta_anchor_hash,
            },
            "provenance_anchor_hash": beta_anchor_hash,
            "tier_mode": "macro",
            "deterministic_fingerprint": "",
            "extensions": {
                "source_process_id": "process.system_collapse",
                "placeholder_assembly_id": "assembly.system_capsule_placeholder.system.engine.beta",
                "captured_assembly_ids": [
                    "assembly.engine.root.beta",
                    "assembly.engine.pump.beta",
                    "assembly.engine.generator.beta",
                ],
                "boundary_invariant_ids": [
                    "invariant.mass_conserved",
                    "invariant.energy_conserved",
                    "invariant.pollutant_accounted",
                ],
            },
        }
    ]
    state["assembly_rows"] = sorted(
        [dict(row) for row in list(state.get("assembly_rows") or []) if isinstance(row, Mapping)]
        + [
            {
                "schema_version": "1.0.0",
                "assembly_id": "assembly.system_capsule_placeholder.system.engine.beta",
                "assembly_type_id": "assembly.system.capsule_placeholder",
                "deterministic_fingerprint": "",
                "extensions": {
                    "source_process_id": "process.system_collapse",
                    "system_id": "system.engine.beta",
                    "capsule_id": "capsule.system.engine.beta",
                    "interface_signature_id": "iface.system.engine.beta",
                },
            }
        ],
        key=lambda row: str(row.get("assembly_id", "")),
    )

    state.setdefault("system_collapse_event_rows", [])
    state.setdefault("system_expand_event_rows", [])
    state.setdefault("system_tier_change_event_rows", [])
    state.setdefault("control_decision_log", [])
    state.setdefault("explain_artifact_rows", [])
    state.setdefault("system_tier_change_hash_chain", "")
    state.setdefault("collapse_expand_event_hash_chain", "")
    return state


def micro_only_state() -> dict:
    state = copy.deepcopy(sys0_cloned_state())
    state.setdefault("system_collapse_event_rows", [])
    state.setdefault("system_expand_event_rows", [])
    state.setdefault("system_macro_capsule_rows", [])
    state.setdefault("system_state_vector_rows", [])
    state.setdefault("system_tier_change_event_rows", [])
    state.setdefault("control_decision_log", [])
    state.setdefault("explain_artifact_rows", [])
    state.setdefault("system_tier_change_hash_chain", "")
    state.setdefault("collapse_expand_event_hash_chain", "")
    return state


def execute_system_roi_tick(
    *,
    repo_root: str,
    state: dict,
    inputs: Mapping[str, object] | None = None,
    policy_context: Mapping[str, object] | None = None,
) -> dict:
    import sys

    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys3.system_roi_tick.{}".format(
                canonical_sha256(dict(inputs or {}))[:12]
            ),
            "process_id": "process.system_roi_tick",
            "inputs": dict(inputs or {}),
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_context or {}),
    )

