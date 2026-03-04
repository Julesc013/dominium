"""FAST test: proper-time mapping is deterministic for equivalent inputs."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_proper_time_mapping_deterministic"
TEST_TAGS = ["fast", "time", "temp1", "determinism"]


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError) as exc:
        return {}, str(exc)


def _run_eval(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.models import model_type_rows_by_id
    from src.time import evaluate_time_mappings

    temporal_payload, temporal_error = _load_json(repo_root, "data/registries/temporal_domain_registry.json")
    mapping_payload, mapping_error = _load_json(repo_root, "data/registries/time_mapping_registry.json")
    model_payload, model_error = _load_json(repo_root, "data/registries/constitutive_model_registry.json")
    model_type_payload, model_type_error = _load_json(repo_root, "data/registries/model_type_registry.json")
    if temporal_error or mapping_error or model_error or model_type_error:
        return {}

    mapping_rows = [
        dict(row)
        for row in list(((mapping_payload.get("record") or {}).get("time_mappings") or []))
        if isinstance(row, dict) and str(row.get("mapping_id", "")).strip() == "mapping.proper_default_stub"
    ]
    if not mapping_rows:
        return {}

    model_rows = list(((model_payload.get("record") or {}).get("models") or []))
    model_type_rows = model_type_rows_by_id(model_type_payload)

    return evaluate_time_mappings(
        current_tick=12,
        time_mapping_rows=mapping_rows,
        temporal_domain_rows=list(((temporal_payload.get("record") or {}).get("temporal_domains") or [])),
        model_rows=model_rows,
        model_type_rows=model_type_rows,
        existing_cache_rows=[],
        existing_time_stamp_rows=[],
        existing_proper_time_rows=[],
        scope_rows_by_selector={
            "per_assembly": ["assembly.temp1.alpha"],
        },
        input_resolver_fn=lambda _mapping, _scope: {
            "canonical_tick": 12,
            "field.gravity_vector": {"x": 0, "y": -980, "z": 0},
            "velocity": {"x": 125, "y": 0, "z": 0},
        },
        session_id="session.default",
        issuer_subject_id="system.testx.temp1",
        max_cost_units=32,
    )


def run(repo_root: str):
    first = _run_eval(repo_root)
    second = _run_eval(repo_root)
    if not first or not second:
        return {"status": "fail", "message": "failed to evaluate proper-time mapping fixture"}
    if str(first.get("time_mapping_hash_chain", "")) != str(second.get("time_mapping_hash_chain", "")):
        return {"status": "fail", "message": "proper-time hash chain drifted across equivalent runs"}
    if list(first.get("proper_time_rows") or []) != list(second.get("proper_time_rows") or []):
        return {"status": "fail", "message": "proper-time state rows drifted across equivalent runs"}
    proper_rows = [dict(row) for row in list(first.get("proper_time_rows") or []) if isinstance(row, dict)]
    if not proper_rows:
        return {"status": "fail", "message": "proper-time mapping did not emit proper_time_rows"}
    value = int((dict(proper_rows[0])).get("accumulated_proper_time", 0) or 0)
    if value <= 0:
        return {"status": "fail", "message": "proper-time accumulation must be positive for fixture inputs"}
    return {"status": "pass", "message": "proper-time mapping deterministic"}
