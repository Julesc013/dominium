"""FAST test: constitutive model inputs_hash is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_inputs_hash_deterministic"
TEST_TAGS = ["fast", "meta", "model"]


def _evaluate(repo_root: str, *, binding_parameters: dict):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.models.model_engine import evaluate_model_bindings

    model_rows = [
        {
            "schema_version": "1.0.0",
            "model_id": "model.hash",
            "model_type_id": "model_type.signal_attenuation_stub",
            "description": "hash",
            "supported_tiers": ["macro"],
            "input_signature": [
                {"schema_version": "1.0.0", "input_kind": "derived", "input_id": "derived.a", "selector": None, "extensions": {}},
                {"schema_version": "1.0.0", "input_kind": "derived", "input_id": "derived.b", "selector": None, "extensions": {}},
            ],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.out", "extensions": {}}
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
    binding_rows = [
        {
            "schema_version": "1.0.0",
            "binding_id": "binding.hash",
            "model_id": "model.hash",
            "target_kind": "custom",
            "target_id": "target.hash",
            "tier": "macro",
            "parameters": dict(binding_parameters),
            "enabled": True,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    model_type_rows = {
        "model_type.signal_attenuation_stub": {
            "schema_version": "1.0.0",
            "model_type_id": "model_type.signal_attenuation_stub",
            "description": "stub",
            "parameter_schema_id": "dominium.schema.models.model_binding.v1",
            "extensions": {},
        }
    }
    cache_policy_rows = {"cache.none": {"schema_version": "1.0.0", "cache_policy_id": "cache.none", "mode": "none", "ttl_ticks": None, "extensions": {}}}
    resolver = lambda _binding, input_ref: 7 if str(input_ref.get("input_id", "")).endswith(".a") else 13
    return evaluate_model_bindings(
        current_tick=20,
        model_rows=model_rows,
        binding_rows=binding_rows,
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=resolver,
        max_cost_units=4,
    )


def run(repo_root: str):
    eval_a = _evaluate(repo_root, binding_parameters={"x": 1, "y": 2})
    eval_b = _evaluate(repo_root, binding_parameters={"y": 2, "x": 1})
    rows_a = list(eval_a.get("evaluation_results") or [])
    rows_b = list(eval_b.get("evaluation_results") or [])
    if (not rows_a) or (not rows_b):
        return {"status": "fail", "message": "missing evaluation result rows"}
    hash_a = str(rows_a[0].get("inputs_hash", ""))
    hash_b = str(rows_b[0].get("inputs_hash", ""))
    if hash_a != hash_b:
        return {"status": "fail", "message": "inputs_hash changed across equivalent inputs"}
    return {"status": "pass", "message": "inputs_hash deterministic"}

