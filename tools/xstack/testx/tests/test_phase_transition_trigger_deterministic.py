"""FAST test: THERM-2 phase transition model trigger is deterministic."""

from __future__ import annotations

import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_phase_transition_trigger_deterministic"
TEST_TAGS = ["fast", "thermal", "phase", "determinism"]


def _model_rows() -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "model_id": "model.therm.phase.test",
            "model_type_id": "model_type.therm_phase_transition",
            "description": "phase transition deterministic fixture",
            "supported_tiers": ["meso"],
            "input_signature": [
                {"schema_version": "1.0.0", "input_kind": "field", "input_id": "field.temperature", "selector": None, "extensions": {}}
            ],
            "output_signature": [
                {
                    "schema_version": "1.0.0",
                    "output_kind": "derived_quantity",
                    "output_id": "derived.therm.phase_transition_triggered",
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


def _binding_rows() -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "binding_id": "binding.therm.phase.test",
            "model_id": "model.therm.phase.test",
            "target_kind": "custom",
            "target_id": "material.water.batch",
            "tier": "meso",
            "parameters": {
                "current_phase": "liquid",
                "temperature": 26000,
                "freeze_point": 27315,
                "melt_point": 27315,
                "boil_point": 37315,
            },
            "enabled": True,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from models.model_engine import evaluate_model_bindings

    model_type_rows = {
        "model_type.therm_phase_transition": {
            "schema_version": "1.0.0",
            "model_type_id": "model_type.therm_phase_transition",
            "description": "THERM-2 phase transition model type",
            "parameter_schema_id": "dominium.schema.models.model_binding.v1",
            "extensions": {},
        }
    }
    cache_policy_rows = {
        "cache.none": {
            "schema_version": "1.0.0",
            "cache_policy_id": "cache.none",
            "mode": "none",
            "ttl_ticks": None,
            "extensions": {},
        }
    }

    first = evaluate_model_bindings(
        current_tick=42,
        model_rows=_model_rows(),
        binding_rows=_binding_rows(),
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=lambda _binding, _input: 26000,
        max_cost_units=128,
    )
    second = evaluate_model_bindings(
        current_tick=42,
        model_rows=_model_rows(),
        binding_rows=_binding_rows(),
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=lambda _binding, _input: 26000,
        max_cost_units=128,
    )

    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "phase transition model evaluation diverged across identical runs"}

    outputs = [dict(row) for row in list(first.get("output_actions") or []) if isinstance(row, dict)]
    phase_row = next(
        (row for row in outputs if str(row.get("output_id", "")).strip() == "derived.therm.phase_transition_triggered"),
        {},
    )
    if not phase_row:
        return {"status": "fail", "message": "missing derived phase transition output"}
    payload = dict(phase_row.get("payload") or {})
    if not bool(payload.get("transition_triggered", False)):
        return {"status": "fail", "message": "expected transition_triggered=true for below-freeze fixture"}
    if str(payload.get("to_phase", "")).strip() != "solid":
        return {"status": "fail", "message": "expected transition to solid for below-freeze fixture"}
    return {"status": "pass", "message": "phase transition trigger deterministic"}

