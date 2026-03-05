"""Shared SYS-0 TestX fixtures/helpers."""

from __future__ import annotations

import copy
import json
import os


def base_system_state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "process_log": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
        "system_rows": [
            {
                "schema_version": "1.0.0",
                "system_id": "system.engine.alpha",
                "root_assembly_id": "assembly.engine.root.alpha",
                "assembly_ids": [
                    "assembly.engine.root.alpha",
                    "assembly.engine.pump.alpha",
                    "assembly.engine.generator.alpha",
                ],
                "interface_signature_id": "iface.system.engine.alpha",
                "boundary_invariant_ids": [
                    "invariant.mass_conserved",
                    "invariant.energy_conserved",
                    "invariant.pollutant_accounted",
                ],
                "tier_contract_id": "tier.system.default",
                "current_tier": "micro",
                "active_capsule_id": "",
                "deterministic_fingerprint": "",
                "extensions": {
                    "macro_model_bindings": [
                        {"model_id": "model.system.engine.stub", "role": "boundary"}
                    ],
                    "boundary_invariant_template_ids": [
                        "inv.mass_energy_basic",
                        "inv.energy_pollution_basic",
                    ],
                    "safety_pattern_ids": [
                        "safety.fail_safe_stop",
                    ],
                    "emits_pollutants": True,
                    "unresolved_hazard_count": 0,
                    "pending_internal_event_count": 0,
                    "open_branch_dependency_count": 0,
                },
            }
        ],
        "system_interface_signature_rows": [
            {
                "schema_version": "1.0.0",
                "system_id": "system.engine.alpha",
                "interface_signature_id": "iface.system.engine.alpha",
                "port_list": [
                    {
                        "port_id": "port.fuel_in",
                        "port_type_id": "port.fluid.fuel",
                        "direction": "in",
                        "allowed_bundle_ids": ["bundle.fluid_basic"],
                        "spec_limit_refs": ["spec.vehicle_interface"],
                    },
                    {
                        "port_id": "port.power_out",
                        "port_type_id": "port.power.output",
                        "direction": "out",
                        "allowed_bundle_ids": ["bundle.power_phasor"],
                        "spec_limit_refs": ["spec.vehicle_interface"],
                    },
                ],
                "signal_descriptors": [
                    {
                        "channel_type_id": "channel.wired_basic",
                        "capacity": 1024,
                        "delay": 1,
                        "access_policy_id": "ctrl.policy.player.diegetic",
                    }
                ],
                "signal_channels": [
                    {"channel_id": "sig.engine.control", "direction": "bidir"}
                ],
                "spec_compliance_ref": "spec.vehicle_interface",
                "spec_limits": {
                    "max_pressure": 1000,
                    "max_temperature": 1200,
                },
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "system_boundary_invariant_rows": [
            {
                "schema_version": "1.0.0",
                "invariant_id": "invariant.mass_conserved",
                "quantity_ids": ["quantity.mass"],
                "invariant_kind": "mass",
                "tolerance_policy_id": "tol.strict",
                "boundary_flux_allowed": True,
                "ledger_transform_required": False,
                "deterministic_fingerprint": "",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "invariant_id": "invariant.energy_conserved",
                "quantity_ids": ["quantity.energy"],
                "invariant_kind": "energy",
                "tolerance_policy_id": "tol.strict",
                "boundary_flux_allowed": True,
                "ledger_transform_required": True,
                "deterministic_fingerprint": "",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "invariant_id": "invariant.pollutant_accounted",
                "quantity_ids": ["quantity.pollutant_mass"],
                "invariant_kind": "pollution",
                "tolerance_policy_id": "tol.default",
                "boundary_flux_allowed": True,
                "ledger_transform_required": False,
                "deterministic_fingerprint": "",
                "extensions": {},
            },
        ],
        "system_macro_capsule_rows": [],
        "system_state_vector_rows": [],
        "system_collapse_event_rows": [],
        "system_expand_event_rows": [],
        "assembly_rows": [
            {
                "schema_version": "1.0.0",
                "assembly_id": "assembly.engine.root.alpha",
                "assembly_type_id": "assembly.engine.root",
                "deterministic_fingerprint": "",
                "extensions": {"powertrain_role": "root"},
            },
            {
                "schema_version": "1.0.0",
                "assembly_id": "assembly.engine.pump.alpha",
                "assembly_type_id": "assembly.pump",
                "deterministic_fingerprint": "",
                "extensions": {"powertrain_role": "pump"},
            },
            {
                "schema_version": "1.0.0",
                "assembly_id": "assembly.engine.generator.alpha",
                "assembly_type_id": "assembly.generator",
                "deterministic_fingerprint": "",
                "extensions": {"powertrain_role": "generator"},
            },
        ],
    }


def law_profile() -> dict:
    return {
        "law_profile_id": "law.sys0.test",
        "allowed_processes": [
            "process.system_collapse",
            "process.system_expand",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.system_collapse": "session.boot",
            "process.system_expand": "session.boot",
        },
        "process_privilege_requirements": {
            "process.system_collapse": "observer",
            "process.system_expand": "observer",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.sys0.test",
        "entitlements": ["session.boot"],
        "privilege_level": "observer",
    }


def execute_system_process(*, state: dict, process_id: str, inputs: dict) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.sys0.{}.{}".format(
                process_id.replace(".", "_"),
                str(inputs.get("system_id") or inputs.get("capsule_id") or "id").replace(".", "_"),
            ),
            "process_id": process_id,
            "inputs": dict(inputs or {}),
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context={},
    )


def cloned_state() -> dict:
    return copy.deepcopy(base_system_state())


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


def validation_registry_payloads(*, repo_root: str) -> dict:
    return {
        "quantity_bundle_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/quantity_bundle_registry.json",
        ),
        "spec_type_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/spec_type_registry.json",
        ),
        "signal_channel_type_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/signal_channel_type_registry.json",
        ),
        "boundary_invariant_template_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/boundary_invariant_template_registry.json",
        ),
        "tolerance_policy_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/tolerance_policy_registry.json",
        ),
        "safety_pattern_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/safety_pattern_registry.json",
        ),
        "macro_model_set_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/macro_model_set_registry.json",
        ),
        "constitutive_model_registry_payload": _read_registry_payload(
            repo_root=repo_root,
            rel_path="data/registries/constitutive_model_registry.json",
        ),
    }
