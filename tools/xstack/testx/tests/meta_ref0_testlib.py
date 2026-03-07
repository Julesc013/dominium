"""Shared META-REF0 TestX fixtures/helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Iterable, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


_REGISTRY_REL = "data/registries/reference_evaluator_registry.json"


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def load_reference_registry(repo_root: str) -> dict:
    abs_path = os.path.join(repo_root, _REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, Mapping) else {}


def active_evaluator_ids(repo_root: str) -> list[str]:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.meta.reference import reference_evaluator_rows_by_id

    by_id = reference_evaluator_rows_by_id(load_reference_registry(repo_root))
    out = []
    for evaluator_id in sorted(by_id.keys()):
        row = dict(by_id.get(evaluator_id) or {})
        status = str(_as_map(row.get("extensions")).get("status", "active")).strip().lower() or "active"
        if status == "active":
            out.append(evaluator_id)
    return out


def fixture_state(seed: int = 1107, tick_start: int = 0, tick_end: int = 3) -> dict:
    tick_a = int(max(0, _as_int(tick_start, 0)))
    tick_b = int(max(tick_a, _as_int(tick_end, tick_a)))

    model_payload = {"nodes": [{"node_id": "node.input", "op": "input"}], "seed": int(seed)}
    payload_hash = canonical_sha256(model_payload)
    source_hash = canonical_sha256({"source_kind": "model_set", "seed": int(seed)})
    proof_hash = canonical_sha256(
        {
            "source_hash": source_hash,
            "compiled_payload_hash": payload_hash,
            "proof_kind": "exact",
            "verification_procedure_id": "verify.exact_structural",
            "error_bound_policy_id": None,
        }
    )

    entries = []
    for index in range(6):
        tick_value = int(tick_a + (index % 3))
        input_energy = int(100 + ((seed + index) % 11))
        output_energy = int(90 + ((seed + index) % 11))
        entries.append(
            {
                "schema_version": "1.0.0",
                "entry_id": "ledger.energy.ref.{}".format(index),
                "tick": tick_value,
                "transformation_id": "transform.ref.energy",
                "source_id": "source.ref.{}".format(index % 2),
                "input_values": {"quantity.energy_total": input_energy},
                "output_values": {"quantity.energy_total": output_energy},
                "energy_total_delta": int(output_energy - input_energy),
            }
        )

    return {
        "energy_ledger_entries": entries,
        "model_rows": [
            {
                "schema_version": "1.0.0",
                "model_id": "model.ref.alpha",
                "model_type_id": "model_type.ref.stub",
                "cache_policy_id": "cache.none",
                "supported_tiers": ["macro"],
                "input_signature": [{"input_kind": "derived", "input_id": "input.alpha", "selector": None}],
                "output_signature": [{"output_kind": "derived_quantity", "output_id": "quantity.ref.alpha"}],
                "cost_units": 4,
                "uses_rng_stream": False,
                "rng_stream_name": "",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "model_id": "model.ref.beta",
                "model_type_id": "model_type.ref.stub",
                "cache_policy_id": "cache.none",
                "supported_tiers": ["macro"],
                "input_signature": [{"input_kind": "derived", "input_id": "input.beta", "selector": None}],
                "output_signature": [{"output_kind": "derived_quantity", "output_id": "quantity.ref.beta"}],
                "cost_units": 5,
                "uses_rng_stream": False,
                "rng_stream_name": "",
                "extensions": {},
            },
        ],
        "model_binding_rows": [
            {
                "binding_id": "binding.ref.alpha",
                "model_id": "model.ref.alpha",
                "target_kind": "custom",
                "target_id": "target.ref.alpha",
                "tier": "macro",
                "parameters": {},
                "enabled": True,
                "extensions": {},
            },
            {
                "binding_id": "binding.ref.beta",
                "model_id": "model.ref.beta",
                "target_kind": "custom",
                "target_id": "target.ref.beta",
                "tier": "macro",
                "parameters": {},
                "enabled": True,
                "extensions": {},
            },
        ],
        "model_type_rows": {"model_type.ref.stub": {"model_type_id": "model_type.ref.stub"}},
        "cache_policy_rows": {"cache.none": {"cache_policy_id": "cache.none", "mode": "none", "ttl_ticks": None}},
        "max_cost_units": 9,
        "far_target_ids": [],
        "far_tick_stride": 4,
        "system_rows": [
            {
                "system_id": "system.ref.alpha",
                "boundary_invariant_ids": ["invariant.ref.mass", "invariant.ref.energy"],
                "extensions": {
                    "boundary_invariant_template_ids": ["inv.ref.mass_energy"],
                    "safety_pattern_ids": ["safety.ref.fail_safe"],
                    "emits_pollutants": False,
                },
            }
        ],
        "system_boundary_invariant_rows": [
            {
                "invariant_id": "invariant.ref.mass",
                "invariant_kind": "mass",
                "tolerance_policy_id": "tol.default",
                "boundary_flux_allowed": True,
                "ledger_transform_required": False,
            },
            {
                "invariant_id": "invariant.ref.energy",
                "invariant_kind": "energy",
                "tolerance_policy_id": "tol.default",
                "boundary_flux_allowed": True,
                "ledger_transform_required": True,
            },
        ],
        "boundary_invariant_template_registry_payload": {
            "record": {
                "boundary_invariant_templates": [
                    {
                        "boundary_invariant_template_id": "inv.ref.mass_energy",
                        "required_invariants": ["invariant.ref.mass", "invariant.ref.energy"],
                        "required_safety_pattern_ids": ["safety.ref.fail_safe"],
                    }
                ]
            }
        },
        "tolerance_policy_registry_payload": {"record": {"tolerance_policies": [{"tolerance_policy_id": "tol.default"}]}},
        "safety_pattern_registry_payload": {"record": {"safety_patterns": [{"pattern_id": "safety.ref.fail_safe"}]}},
        "compiled_model_rows": [
            {
                "compiled_model_id": "compiled_model.ref.alpha",
                "source_kind": "model_set",
                "source_hash": source_hash,
                "compiled_type_id": "compiled.reduced_graph",
                "compiled_payload_ref": {"payload": model_payload, "payload_hash": payload_hash},
                "input_signature_ref": "signature.input.ref.alpha",
                "output_signature_ref": "signature.output.ref.alpha",
                "validity_domain_ref": "validity_domain.ref.alpha",
                "equivalence_proof_ref": "proof.ref.alpha",
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "equivalence_proof_rows": [
            {
                "proof_id": "proof.ref.alpha",
                "proof_kind": "exact",
                "verification_procedure_id": "verify.exact_structural",
                "error_bound_policy_id": None,
                "proof_hash": proof_hash,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
        "current_tick": int(tick_b),
    }


def run_reference_suite_case(
    *,
    repo_root: str,
    seed: int = 1107,
    tick_start: int = 0,
    tick_end: int = 3,
    evaluator_ids: Iterable[str] | None = None,
    state_payload: Mapping[str, object] | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.meta.reference import evaluate_reference_suite

    selected = _sorted_tokens(evaluator_ids or active_evaluator_ids(repo_root))
    payload = dict(state_payload or fixture_state(seed=seed, tick_start=tick_start, tick_end=tick_end))
    current_tick = int(max(_as_int(tick_start, 0), _as_int(tick_end, 0)))
    return evaluate_reference_suite(
        evaluator_ids=selected,
        state_payload=payload,
        current_tick=current_tick,
        seed=int(seed),
        tick_start=int(tick_start),
        tick_end=int(tick_end),
        configs_by_evaluator_id={},
    )


def run_reference_evaluator_case(
    *,
    repo_root: str,
    evaluator_id: str,
    seed: int = 1107,
    tick_start: int = 0,
    tick_end: int = 3,
    state_payload: Mapping[str, object] | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.meta.reference import evaluate_reference_evaluator

    payload = dict(state_payload or fixture_state(seed=seed, tick_start=tick_start, tick_end=tick_end))
    current_tick = int(max(_as_int(tick_start, 0), _as_int(tick_end, 0)))
    return evaluate_reference_evaluator(
        evaluator_id=str(evaluator_id),
        state_payload=payload,
        current_tick=current_tick,
        seed=int(seed),
        tick_start=int(tick_start),
        tick_end=int(tick_end),
        config={},
    )
