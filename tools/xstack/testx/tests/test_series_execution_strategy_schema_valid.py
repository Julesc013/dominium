"""FAST test: PI-1 strategy artifact exposes the expected structure."""

from __future__ import annotations


TEST_ID = "test_series_execution_strategy_schema_valid"
TEST_TAGS = ["fast", "pi", "blueprint", "strategy"]


def run(repo_root: str):
    from tools.xstack.testx.tests.series_execution_strategy_testlib import committed_series_execution_strategy, fresh_snapshot

    committed = committed_series_execution_strategy(repo_root)
    fresh = dict(fresh_snapshot(repo_root).get("series_execution_strategy") or {})
    if str(committed.get("report_id", "")).strip() != "pi.1.series_execution_strategy.v1":
        return {"status": "fail", "message": "strategy report_id drifted"}
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "strategy fingerprint drifted on regeneration"}
    if list(committed.get("phase_order") or []) != ["A", "B", "C", "D", "E"]:
        return {"status": "fail", "message": "phase order must remain A-E"}
    if len(list(committed.get("priority_bands") or [])) < 4:
        return {"status": "fail", "message": "priority bands are incomplete"}
    capability_rows = list(committed.get("capability_foundations") or [])
    if not capability_rows:
        return {"status": "fail", "message": "capability foundations are missing"}
    first = dict(capability_rows[0] or {})
    for key in ("capability_id", "required_foundations", "required_series", "execution_phase", "planning_bucket"):
        if key not in first:
            return {"status": "fail", "message": f"capability row missing '{key}'"}
    if not str(committed.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "strategy missing deterministic_fingerprint"}
    return {"status": "pass", "message": "PI-1 strategy artifact exposes the expected structure"}
