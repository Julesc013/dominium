"""FAST test: PROC-6 drift scoring is deterministic for equivalent inputs."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_drift_score_deterministic"
TEST_TAGS = ["fast", "proc", "proc6", "drift", "determinism"]


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.drift import drift_policy_rows_by_id, evaluate_process_drift

    registry = _load_json(repo_root, "data/registries/process_drift_policy_registry.json")
    policy = dict(drift_policy_rows_by_id(registry).get("drift.default") or {})
    if not policy:
        return {"status": "fail", "message": "missing drift.default policy"}

    kwargs = {
        "current_tick": 202,
        "process_id": "proc.test.proc6.deterministic",
        "version": "1.0.0",
        "drift_policy_row": policy,
        "previous_metrics_row": {
            "qc_pass_rate": 980,
            "yield_variance": 120,
        },
        "metrics_row": {
            "qc_pass_rate": 820,
            "yield_variance": 3720,
        },
        "environment_deviation_score": 220,
        "tool_degradation_score": 300,
        "calibration_deviation_score": 140,
        "entropy_growth_rate": 260,
        "reliability_failure_count": 1,
        "update_stride": 1,
        "force_update": True,
    }
    first = evaluate_process_drift(**kwargs)
    second = evaluate_process_drift(**kwargs)

    if first != second:
        return {"status": "fail", "message": "drift evaluation output mismatch across equivalent calls"}
    band = str((dict(first.get("drift_state_row") or {})).get("drift_band", "")).strip()
    if band not in {"drift.normal", "drift.warning", "drift.critical"}:
        return {"status": "fail", "message": "invalid drift band produced: {}".format(band)}
    score = int((dict(first.get("drift_state_row") or {})).get("drift_score", -1))
    if score < 0 or score > 1000:
        return {"status": "fail", "message": "drift score out of range"}
    return {"status": "pass", "message": "PROC-6 drift scoring deterministic for equivalent inputs"}

