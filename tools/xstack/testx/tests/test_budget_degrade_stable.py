"""FAST test: model budget degradation order is deterministic and stable."""

from __future__ import annotations

import sys


TEST_ID = "test_budget_degrade_stable"
TEST_TAGS = ["fast", "meta", "model", "budget"]


def _evaluate(repo_root: str, binding_order: list[str]):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from models.model_engine import evaluate_model_bindings

    model_rows = [
        {
            "schema_version": "1.0.0",
            "model_id": "model.budget",
            "model_type_id": "model_type.signal_attenuation_stub",
            "description": "budget",
            "supported_tiers": ["macro"],
            "input_signature": [{"schema_version": "1.0.0", "input_kind": "derived", "input_id": "d", "selector": None, "extensions": {}}],
            "output_signature": [{"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "q", "extensions": {}}],
            "cost_units": 2,
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
            "binding_id": token,
            "model_id": "model.budget",
            "target_kind": "custom",
            "target_id": "target.{}".format(token),
            "tier": "macro",
            "parameters": {},
            "enabled": True,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        for token in binding_order
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
    return evaluate_model_bindings(
        current_tick=50,
        model_rows=model_rows,
        binding_rows=binding_rows,
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=(lambda _binding, _input: 1),
        max_cost_units=4,
    )


def run(repo_root: str):
    eval_a = _evaluate(repo_root, ["binding.4", "binding.2", "binding.1", "binding.3"])
    eval_b = _evaluate(repo_root, ["binding.3", "binding.1", "binding.4", "binding.2"])
    processed_a = list(eval_a.get("processed_binding_ids") or [])
    processed_b = list(eval_b.get("processed_binding_ids") or [])
    if processed_a != processed_b:
        return {"status": "fail", "message": "processed bindings differ under same budget"}
    deferred_a = [str(dict(row).get("binding_id", "")) for row in list(eval_a.get("deferred_rows") or [])]
    deferred_b = [str(dict(row).get("binding_id", "")) for row in list(eval_b.get("deferred_rows") or [])]
    if deferred_a != deferred_b:
        return {"status": "fail", "message": "deferred rows differ under same budget"}
    if str(eval_a.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected degraded budget outcome"}
    return {"status": "pass", "message": "budget degradation order stable"}

