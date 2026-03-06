"""FAST test: PROC-4 stabilization scoring is deterministic."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_stabilization_score_deterministic"
TEST_TAGS = ["fast", "proc", "maturity", "determinism"]


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

    from src.process.maturity.metrics_engine import (
        build_process_metrics_state_row,
        stabilization_policy_rows_by_id,
    )
    from src.process.maturity.maturity_engine import compute_stabilization_score

    registry = _load_json(repo_root, "data/registries/stabilization_policy_registry.json")
    policy = dict(stabilization_policy_rows_by_id(registry).get("stab.default") or {})
    if not policy:
        return {"status": "fail", "message": "missing stab.default policy row"}
    metrics = build_process_metrics_state_row(
        process_id="proc.test.proc4.score",
        version="1.0.0",
        runs_count=20,
        yield_mean=955,
        yield_variance=8,
        defect_rate=12,
        qc_pass_rate=980,
        env_deviation_score=4,
        calibration_deviation_score=2,
        last_update_tick=900,
    )
    score_first = compute_stabilization_score(
        metrics_row=metrics, stabilization_policy_row=policy
    )
    score_second = compute_stabilization_score(
        metrics_row=metrics, stabilization_policy_row=policy
    )
    if score_first != score_second:
        return {"status": "fail", "message": "stabilization score mismatch across equivalent calls"}
    if not (0 <= int(score_first) <= 1000):
        return {"status": "fail", "message": "stabilization score out of expected range"}
    if int(score_first) < int(policy.get("thresholds", {}).get("certified", 0)):
        return {"status": "fail", "message": "fixture did not reach certified threshold under stab.default"}
    return {"status": "pass", "message": "PROC-4 stabilization score is deterministic"}
