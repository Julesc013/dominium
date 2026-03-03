"""FAST test: model RNG path is used only when declared by model."""

from __future__ import annotations

import sys


TEST_ID = "test_rng_usage_only_when_declared"
TEST_TAGS = ["fast", "meta", "model", "rng"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.models.model_engine import evaluate_model_bindings

    model_rows = [
        {
            "schema_version": "1.0.0",
            "model_id": "model.no_rng",
            "model_type_id": "model_type.signal_attenuation_stub",
            "description": "no rng",
            "supported_tiers": ["macro"],
            "input_signature": [{"schema_version": "1.0.0", "input_kind": "derived", "input_id": "d", "selector": None, "extensions": {}}],
            "output_signature": [{"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "q", "extensions": {}}],
            "cost_units": 1,
            "cache_policy_id": "cache.none",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.with_rng",
            "model_type_id": "model_type.signal_attenuation_stub",
            "description": "with rng",
            "supported_tiers": ["macro"],
            "input_signature": [{"schema_version": "1.0.0", "input_kind": "derived", "input_id": "d", "selector": None, "extensions": {}}],
            "output_signature": [{"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "q", "extensions": {}}],
            "cost_units": 1,
            "cache_policy_id": "cache.none",
            "uses_rng_stream": True,
            "rng_stream_name": "rng.model.test",
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
    ]
    binding_rows = [
        {"schema_version": "1.0.0", "binding_id": "binding.a", "model_id": "model.no_rng", "target_kind": "custom", "target_id": "target.a", "tier": "macro", "parameters": {}, "enabled": True, "deterministic_fingerprint": "", "extensions": {}},
        {"schema_version": "1.0.0", "binding_id": "binding.b", "model_id": "model.with_rng", "target_kind": "custom", "target_id": "target.b", "tier": "macro", "parameters": {}, "enabled": True, "deterministic_fingerprint": "", "extensions": {}},
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
    resolver = lambda _binding, _input: 9
    evaluated = evaluate_model_bindings(
        current_tick=40,
        model_rows=model_rows,
        binding_rows=binding_rows,
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=resolver,
        max_cost_units=8,
    )
    by_binding = dict(
        (
            str(dict(row.get("extensions") or {}).get("binding_id", "")),
            bool(dict(row.get("extensions") or {}).get("rng_used", False)),
        )
        for row in list(evaluated.get("observation_rows") or [])
        if isinstance(row, dict)
    )
    if by_binding.get("binding.a", True):
        return {"status": "fail", "message": "rng_used should be false for binding.a"}
    if not by_binding.get("binding.b", False):
        return {"status": "fail", "message": "rng_used should be true for binding.b"}
    return {"status": "pass", "message": "rng usage occurs only when model declares a stream"}

