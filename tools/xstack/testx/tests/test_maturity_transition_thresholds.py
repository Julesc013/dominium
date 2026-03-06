"""FAST test: PROC-4 maturity transitions follow deterministic thresholds."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_maturity_transition_thresholds"
TEST_TAGS = ["fast", "proc", "maturity", "thresholds"]


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
    from src.process.maturity.maturity_engine import (
        evaluate_process_maturity,
        process_lifecycle_policy_rows_by_id,
    )

    stabilization_registry = _load_json(repo_root, "data/registries/stabilization_policy_registry.json")
    lifecycle_registry = _load_json(
        repo_root, "data/registries/process_lifecycle_policy_registry.json"
    )
    policy = dict(stabilization_policy_rows_by_id(stabilization_registry).get("stab.default") or {})
    lifecycle = dict(
        process_lifecycle_policy_rows_by_id(lifecycle_registry).get("proc.lifecycle.default") or {}
    )
    if not policy:
        return {"status": "fail", "message": "missing stab.default policy"}
    if not lifecycle:
        return {"status": "fail", "message": "missing proc.lifecycle.default policy"}

    metrics = build_process_metrics_state_row(
        process_id="proc.test.proc4.lifecycle",
        version="1.0.0",
        runs_count=40,
        yield_mean=980,
        yield_variance=3,
        defect_rate=0,
        qc_pass_rate=1000,
        env_deviation_score=0,
        calibration_deviation_score=0,
        last_update_tick=1000,
    )
    first = evaluate_process_maturity(
        current_tick=1000,
        process_id="proc.test.proc4.lifecycle",
        version="1.0.0",
        metrics_row=metrics,
        previous_maturity_state="exploration",
        previous_state_extensions={},
        stabilization_policy_row=policy,
        lifecycle_policy_row=lifecycle,
        certification_gate_passed=True,
        certification_required=False,
    )
    if str(first.get("next_maturity_state", "")).strip() != "certified":
        return {
            "status": "fail",
            "message": "expected first transition to reach certified before stability horizon",
        }
    first_extensions = dict(first.get("state_extensions") or {})
    horizon = int(max(0, int(policy.get("stability_horizon_ticks", 0))))
    second = evaluate_process_maturity(
        current_tick=1000 + max(1, horizon),
        process_id="proc.test.proc4.lifecycle",
        version="1.0.0",
        metrics_row=metrics,
        previous_maturity_state=str(first.get("next_maturity_state", "exploration")),
        previous_state_extensions=first_extensions,
        stabilization_policy_row=policy,
        lifecycle_policy_row=lifecycle,
        certification_gate_passed=True,
        certification_required=False,
    )
    if str(second.get("next_maturity_state", "")).strip() != "capsule_eligible":
        return {"status": "fail", "message": "expected transition to capsule_eligible after stability horizon"}
    return {"status": "pass", "message": "PROC-4 maturity transitions obey deterministic thresholds"}
