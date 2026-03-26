"""FAST test: PI-1 stop conditions cover every execution phase."""

from __future__ import annotations


TEST_ID = "test_stop_conditions_present_for_each_phase"
TEST_TAGS = ["fast", "pi", "blueprint", "stops"]


def run(repo_root: str):
    from tools.xstack.testx.tests.series_execution_strategy_testlib import committed_stop_conditions

    payload = committed_stop_conditions(repo_root)
    entries = list(payload.get("entries") or [])
    seen = {str(dict(row).get("phase_id", "")).strip() for row in entries if str(dict(row).get("phase_id", "")).strip()}
    missing = [phase_id for phase_id in ("A", "B", "C", "D", "E") if phase_id not in seen]
    if missing:
        return {"status": "fail", "message": f"missing stop condition coverage for phases: {', '.join(missing)}"}
    for row in entries:
        current = dict(row)
        if not list(current.get("hard_stop_conditions") or []):
            return {"status": "fail", "message": "each stop condition entry must list hard_stop_conditions"}
    return {"status": "pass", "message": "PI-1 stop conditions cover every phase"}
