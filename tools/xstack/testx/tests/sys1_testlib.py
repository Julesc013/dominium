"""Shared SYS-1 validation fixtures/helpers."""

from __future__ import annotations

import copy

from tools.xstack.testx.tests.sys0_testlib import (
    cloned_state as sys0_cloned_state,
    validation_registry_payloads,
)


def cloned_state() -> dict:
    return copy.deepcopy(sys0_cloned_state())


def validation_payloads(*, repo_root: str) -> dict:
    return dict(validation_registry_payloads(repo_root=repo_root))


def macro_validation_fixture(*, repo_root: str) -> dict:
    state = cloned_state()
    state["system_macro_capsule_rows"] = [
        {
            "schema_version": "1.1.0",
            "capsule_id": "capsule.system.engine.alpha",
            "system_id": "system.engine.alpha",
            "interface_signature_id": "iface.system.engine.alpha",
            "macro_model_bindings": [],
            "macro_model_set_id": "macro.set.engine.stub",
            "model_error_bounds_ref": "tol.strict",
            "internal_state_vector": {"state_vector_id": "statevec.system.engine.alpha"},
            "provenance_anchor_hash": "hash.anchor.sys1.stub",
            "tier_mode": "macro",
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    registries = validation_payloads(repo_root=repo_root)
    registries["macro_model_set_registry_payload"] = {
        "macro_model_sets": [
            {
                "schema_version": "1.0.0",
                "macro_model_set_id": "macro.set.engine.stub",
                "model_bindings": [
                    {
                        "binding_id": "binding.engine.stub",
                        "model_id": "model.sys1.engine.stub",
                        "input_port_ids": ["port.fuel_in"],
                        "output_port_ids": ["port.power_out"],
                    }
                ],
                "error_bound_policy_id": "tol.strict",
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ]
    }
    registries["constitutive_model_registry_payload"] = {
        "constitutive_models": [
            {
                "schema_version": "1.0.0",
                "model_id": "model.sys1.engine.stub",
                "model_type_id": "model.constitutive.stub",
                "description": "SYS-1 test stub model",
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ]
    }
    return {
        "state": state,
        "registries": registries,
        "capsule_id": "capsule.system.engine.alpha",
    }
