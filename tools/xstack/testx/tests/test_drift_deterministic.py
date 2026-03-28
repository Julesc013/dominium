"""FAST test: TEMP-2 drift application is deterministic and policy-driven."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_drift_deterministic"
TEST_TAGS = ["fast", "time", "temp2", "determinism"]


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError) as exc:
        return {}, str(exc)


def _run_eval(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from models import model_type_rows_by_id
    from engine.time import evaluate_time_mappings, normalize_drift_policy_rows

    temporal_payload, temporal_error = _load_json(repo_root, "data/registries/temporal_domain_registry.json")
    mapping_payload, mapping_error = _load_json(repo_root, "data/registries/time_mapping_registry.json")
    model_payload, model_error = _load_json(repo_root, "data/registries/constitutive_model_registry.json")
    model_type_payload, model_type_error = _load_json(repo_root, "data/registries/model_type_registry.json")
    drift_payload, drift_error = _load_json(repo_root, "data/registries/drift_policy_registry.json")
    if temporal_error or mapping_error or model_error or model_type_error or drift_error:
        return {}

    mapping_rows = [
        dict(row)
        for row in list(((mapping_payload.get("record") or {}).get("time_mappings") or []))
        if isinstance(row, dict) and str(row.get("mapping_id", "")).strip() == "mapping.proper_default_stub"
    ]
    if not mapping_rows:
        return {}
    mapping_rows[0]["drift_policy_id"] = "drift.linear_small"

    drift_rows = normalize_drift_policy_rows(
        list(((drift_payload.get("record") or {}).get("drift_policies") or []))
    )
    return evaluate_time_mappings(
        current_tick=10,
        time_mapping_rows=mapping_rows,
        temporal_domain_rows=list(((temporal_payload.get("record") or {}).get("temporal_domains") or [])),
        model_rows=list(((model_payload.get("record") or {}).get("models") or [])),
        model_type_rows=model_type_rows_by_id(model_type_payload),
        drift_policy_rows=drift_rows,
        existing_cache_rows=[],
        existing_time_stamp_rows=[],
        existing_proper_time_rows=[],
        scope_rows_by_selector={"per_assembly": ["assembly.temp2.alpha"]},
        input_resolver_fn=lambda _mapping, _scope: {
            "canonical_tick": 10,
            "field.gravity_vector": {"x": 0, "y": -980, "z": 0},
            "velocity": {"x": 100, "y": 0, "z": 0},
        },
        session_id="session.default",
        issuer_subject_id="system.testx.temp2",
        max_cost_units=64,
    )


def run(repo_root: str):
    first = _run_eval(repo_root)
    second = _run_eval(repo_root)
    if not first or not second:
        return {"status": "fail", "message": "failed to evaluate drift mapping fixture"}
    if str(first.get("time_mapping_hash_chain", "")) != str(second.get("time_mapping_hash_chain", "")):
        return {"status": "fail", "message": "drift mapping hash chain drifted across equivalent runs"}
    drift_ids = list(first.get("active_drift_policy_ids") or [])
    if "drift.linear_small" not in set(str(item).strip() for item in drift_ids):
        return {"status": "fail", "message": "active_drift_policy_ids missing drift.linear_small"}
    values = [dict(row) for row in list(first.get("value_rows") or []) if isinstance(row, dict)]
    if not values:
        return {"status": "fail", "message": "drift mapping produced no value rows"}
    delta = int(values[0].get("delta_domain_time", 0) or 0)
    if delta <= 0:
        return {"status": "fail", "message": "drifted delta_domain_time must remain positive"}
    return {"status": "pass", "message": "drift mapping deterministic"}
