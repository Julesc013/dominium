"""FAST test: model cache reuses outputs by deterministic inputs hash."""

from __future__ import annotations

import sys


TEST_ID = "test_cache_reuse_by_inputs_hash"
TEST_TAGS = ["fast", "meta", "model", "cache"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from models.model_engine import evaluate_model_bindings

    model_rows = [
        {
            "schema_version": "1.0.0",
            "model_id": "model.cache",
            "model_type_id": "model_type.signal_attenuation_stub",
            "description": "cache",
            "supported_tiers": ["macro"],
            "input_signature": [
                {"schema_version": "1.0.0", "input_kind": "derived", "input_id": "d.cache", "selector": None, "extensions": {}}
            ],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "derived.cache", "extensions": {}}
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
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
            "binding_id": "binding.cache",
            "model_id": "model.cache",
            "target_kind": "custom",
            "target_id": "target.cache",
            "tier": "macro",
            "parameters": {},
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
    cache_policy_rows = {
        "cache.by_inputs_hash": {
            "schema_version": "1.0.0",
            "cache_policy_id": "cache.by_inputs_hash",
            "mode": "by_inputs_hash",
            "ttl_ticks": 64,
            "extensions": {},
        }
    }
    resolver = lambda _binding, _input: 5

    first = evaluate_model_bindings(
        current_tick=25,
        model_rows=model_rows,
        binding_rows=binding_rows,
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=resolver,
        max_cost_units=4,
    )
    second = evaluate_model_bindings(
        current_tick=26,
        model_rows=model_rows,
        binding_rows=binding_rows,
        cache_rows=first.get("cache_rows"),
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=resolver,
        max_cost_units=4,
    )

    row_a = dict((list(first.get("evaluation_results") or [{}]))[0])
    row_b = dict((list(second.get("evaluation_results") or [{}]))[0])
    if not row_a or not row_b:
        return {"status": "fail", "message": "missing evaluation rows"}
    if bool(dict(row_a.get("extensions") or {}).get("cache_hit", True)):
        return {"status": "fail", "message": "first evaluation should not be cache_hit"}
    if not bool(dict(row_b.get("extensions") or {}).get("cache_hit", False)):
        return {"status": "fail", "message": "second evaluation should be cache_hit"}
    if str(row_a.get("outputs_hash", "")) != str(row_b.get("outputs_hash", "")):
        return {"status": "fail", "message": "outputs_hash should match on cache reuse"}
    return {"status": "pass", "message": "cache reuse by inputs hash deterministic"}

