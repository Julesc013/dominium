"""FAST test: model binding evaluation order is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_model_binding_order_deterministic"
TEST_TAGS = ["fast", "meta", "model"]


def _model_rows() -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "model_id": "model.a",
            "model_type_id": "model_type.signal_attenuation_stub",
            "description": "a",
            "supported_tiers": ["macro"],
            "input_signature": [
                {"schema_version": "1.0.0", "input_kind": "derived", "input_id": "x", "selector": None, "extensions": {}}
            ],
            "output_signature": [
                {"schema_version": "1.0.0", "output_kind": "derived_quantity", "output_id": "q.a", "extensions": {}}
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


def _bindings(order: list[str]) -> list[dict]:
    rows = []
    for token in order:
        rows.append(
            {
                "schema_version": "1.0.0",
                "binding_id": token,
                "model_id": "model.a",
                "target_kind": "custom",
                "target_id": "target.{}".format(token),
                "tier": "macro",
                "parameters": {},
                "enabled": True,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        )
    return rows


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from models.model_engine import evaluate_model_bindings

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

    resolver = lambda _binding, _input: 1
    eval_a = evaluate_model_bindings(
        current_tick=10,
        model_rows=_model_rows(),
        binding_rows=_bindings(["binding.c", "binding.a", "binding.b"]),
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=resolver,
        max_cost_units=99,
    )
    eval_b = evaluate_model_bindings(
        current_tick=10,
        model_rows=_model_rows(),
        binding_rows=_bindings(["binding.b", "binding.c", "binding.a"]),
        cache_rows=[],
        model_type_rows=model_type_rows,
        cache_policy_rows=cache_policy_rows,
        input_resolver_fn=resolver,
        max_cost_units=99,
    )

    if list(eval_a.get("processed_binding_ids") or []) != list(eval_b.get("processed_binding_ids") or []):
        return {"status": "fail", "message": "processed_binding_ids differ across input order"}
    hashes_a = [str(row.get("inputs_hash", "")) for row in list(eval_a.get("evaluation_results") or [])]
    hashes_b = [str(row.get("inputs_hash", "")) for row in list(eval_b.get("evaluation_results") or [])]
    if hashes_a != hashes_b:
        return {"status": "fail", "message": "inputs_hash ordering differs across input order"}
    return {"status": "pass", "message": "model binding order deterministic"}

