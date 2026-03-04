"""FAST test: civil-time mapping is deterministic and policy-driven."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_civil_time_mapping_deterministic"
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
        if isinstance(row, dict) and str(row.get("mapping_id", "")).strip() == "mapping.civil_calendar_stub"
    ]
    if not mapping_rows:
        return {}
    params = dict(mapping_rows[0].get("parameters") or {})
    ratio = int(params.get("tick_to_seconds_ratio", 1) or 1)
    offset = int(params.get("calendar_offset", 0) or 0)

    evaluation = evaluate_time_mappings(
        current_tick=25,
        time_mapping_rows=mapping_rows,
        temporal_domain_rows=list(((temporal_payload.get("record") or {}).get("temporal_domains") or [])),
        model_rows=list(((model_payload.get("record") or {}).get("models") or [])),
        model_type_rows=model_type_rows_by_id(model_type_payload),
        existing_cache_rows=[],
        existing_time_stamp_rows=[],
        existing_proper_time_rows=[],
        scope_rows_by_selector={"global": ["global"]},
        input_resolver_fn=lambda _mapping, _scope: {"canonical_tick": 25},
        session_id="session.default",
        issuer_subject_id="system.testx.temp1",
        max_cost_units=32,
    )
    expected_value = int(offset + 25 * ratio)
    observed = int((dict(evaluation.get("domain_value_index") or {})).get("time.civil::global", -1))
    return {"evaluation": evaluation, "expected": expected_value, "observed": observed}


def run(repo_root: str):
    first = _run_eval(repo_root)
    second = _run_eval(repo_root)
    if not first or not second:
        return {"status": "fail", "message": "failed to evaluate civil-time mapping fixture"}
    eval_a = dict(first.get("evaluation") or {})
    eval_b = dict(second.get("evaluation") or {})
    if str(eval_a.get("time_mapping_hash_chain", "")) != str(eval_b.get("time_mapping_hash_chain", "")):
        return {"status": "fail", "message": "civil-time hash chain drifted across equivalent runs"}
    if int(first.get("observed", -1)) != int(first.get("expected", -2)):
        return {"status": "fail", "message": "civil-time mapping value does not match ratio/offset policy"}
    if int(second.get("observed", -1)) != int(second.get("expected", -2)):
        return {"status": "fail", "message": "civil-time mapping value drifted on repeated evaluation"}
    return {"status": "pass", "message": "civil-time mapping deterministic"}
