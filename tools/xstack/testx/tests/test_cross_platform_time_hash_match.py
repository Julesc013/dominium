"""STRICT test: TEMP-1 time hash chains are stable across equivalent ordering variants."""

from __future__ import annotations

import json
import os
import re
import sys


TEST_ID = "test_cross_platform_time_hash_match"
TEST_TAGS = ["strict", "time", "temp1", "determinism", "hash"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError) as exc:
        return {}, str(exc)


def _build_variant(repo_root: str, *, reverse_rows: bool) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from models import model_type_rows_by_id
    from engine.time import evaluate_time_mappings
    from tools.time.tool_replay_time_window import verify_time_replay_window

    temporal_payload, temporal_error = _load_json(repo_root, "data/registries/temporal_domain_registry.json")
    mapping_payload, mapping_error = _load_json(repo_root, "data/registries/time_mapping_registry.json")
    model_payload, model_error = _load_json(repo_root, "data/registries/constitutive_model_registry.json")
    model_type_payload, model_type_error = _load_json(repo_root, "data/registries/model_type_registry.json")
    if temporal_error or mapping_error or model_error or model_type_error:
        return {}

    mapping_rows = [dict(row) for row in list(((mapping_payload.get("record") or {}).get("time_mappings") or [])) if isinstance(row, dict)]
    evaluation = evaluate_time_mappings(
        current_tick=33,
        time_mapping_rows=mapping_rows,
        temporal_domain_rows=list(((temporal_payload.get("record") or {}).get("temporal_domains") or [])),
        model_rows=list(((model_payload.get("record") or {}).get("models") or [])),
        model_type_rows=model_type_rows_by_id(model_type_payload),
        existing_cache_rows=[],
        existing_time_stamp_rows=[],
        existing_proper_time_rows=[],
        scope_rows_by_selector={
            "global": ["global"],
            "per_session": ["session.default"],
            "per_assembly": ["assembly.temp1.alpha"],
        },
        input_resolver_fn=lambda _mapping, _scope: {
            "canonical_tick": 33,
            "field.gravity_vector": {"x": 0, "y": -980, "z": 0},
            "velocity": {"x": 240, "y": 0, "z": 0},
            "session_warp_factor": 1750,
        },
        session_id="session.default",
        issuer_subject_id="system.testx.temp1",
        max_cost_units=128,
    )
    domain_index = dict(evaluation.get("domain_value_index") or {})
    schedule_domain_rows = [
        {
            "schema_version": "1.0.0",
            "schedule_id": "schedule.temp1.proper.alpha",
            "target_id": "assembly.temp1.alpha",
            "temporal_domain_id": "time.proper",
            "tick": 33,
            "domain_time_value": int(domain_index.get("time.proper::assembly.temp1.alpha", 0)),
            "target_time_value": 1,
            "due": int(domain_index.get("time.proper::assembly.temp1.alpha", 0)) >= 1,
            "evaluation_policy_id": "schedule.eval.gte_target",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "schedule_id": "schedule.temp1.warp.session",
            "target_id": "session.default",
            "temporal_domain_id": "time.warp",
            "tick": 33,
            "domain_time_value": int(domain_index.get("time.warp::session.default", 0)),
            "target_time_value": 1,
            "due": int(domain_index.get("time.warp::session.default", 0)) >= 1,
            "evaluation_policy_id": "schedule.eval.gte_target",
            "extensions": {},
        },
    ]

    state_payload = {
        "time_mapping_cache_rows": [dict(row) for row in list(evaluation.get("cache_rows") or []) if isinstance(row, dict)],
        "time_stamp_artifacts": [dict(row) for row in list(evaluation.get("time_stamp_rows") or []) if isinstance(row, dict)],
        "proper_time_states": [dict(row) for row in list(evaluation.get("proper_time_rows") or []) if isinstance(row, dict)],
        "schedule_domain_evaluations": [dict(row) for row in schedule_domain_rows],
    }
    if reverse_rows:
        state_payload["time_mapping_cache_rows"] = list(reversed(state_payload["time_mapping_cache_rows"]))
        state_payload["time_stamp_artifacts"] = list(reversed(state_payload["time_stamp_artifacts"]))
        state_payload["proper_time_states"] = list(reversed(state_payload["proper_time_states"]))
        state_payload["schedule_domain_evaluations"] = list(reversed(state_payload["schedule_domain_evaluations"]))

    report = verify_time_replay_window(state_payload=state_payload, expected_payload=None)
    return {"state": state_payload, "report": report}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.time.tool_replay_time_window import verify_time_replay_window

    first = _build_variant(repo_root, reverse_rows=False)
    second = _build_variant(repo_root, reverse_rows=True)
    if not first or not second:
        return {"status": "fail", "message": "failed to evaluate TEMP-1 hash fixture"}

    report_a = dict(first.get("report") or {})
    report_b = dict(second.get("report") or {})
    if str(report_a.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline time replay report failed: {}".format(report_a)}
    if str(report_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "reordered time replay report failed: {}".format(report_b)}

    observed_a = dict(report_a.get("observed") or {})
    observed_b = dict(report_b.get("observed") or {})
    for key in (
        "time_mapping_hash_chain",
        "schedule_domain_evaluation_hash",
        "time_stamp_hash_chain",
        "proper_time_hash_chain",
    ):
        token_a = str(observed_a.get(key, "")).strip().lower()
        token_b = str(observed_b.get(key, "")).strip().lower()
        if (not _HASH64.fullmatch(token_a)) or (not _HASH64.fullmatch(token_b)):
            return {"status": "fail", "message": "invalid hash shape for '{}'".format(key)}
        if token_a != token_b:
            return {"status": "fail", "message": "{} diverged across equivalent ordering variants".format(key)}

    cross = verify_time_replay_window(
        state_payload=dict(first.get("state") or {}),
        expected_payload=dict(second.get("state") or {}),
    )
    if str(cross.get("result", "")) != "complete":
        return {"status": "fail", "message": "cross-variant time replay mismatch: {}".format(cross)}
    return {"status": "pass", "message": "TEMP-1 time hash chains stable across ordering variants"}
