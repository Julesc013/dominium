"""STRICT test: expand/collapse transitions emit deterministic invariant check records."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.reality.invariant_checks_on_collapse_expand"
TEST_TAGS = ["strict", "reality", "transition", "invariants"]

REQUIRED_INVARIANT_IDS = (
    "inv.civ.cohort_size_conservation",
    "inv.conservation.mass_energy_total",
    "inv.transition.expand_materialization",
)


def _event_summary(event_row: dict) -> dict:
    checks = [dict(item) for item in list(event_row.get("invariant_checks") or []) if isinstance(item, dict)]
    return {
        "from_tier": str(event_row.get("from_tier", "")),
        "to_tier": str(event_row.get("to_tier", "")),
        "reason": str(event_row.get("reason", "")),
        "fingerprint_present": bool(str(event_row.get("deterministic_fingerprint", "")).strip()),
        "checks": [
            {
                "invariant_id": str(item.get("invariant_id", "")),
                "status": str(item.get("status", "")),
            }
            for item in sorted(checks, key=lambda row: str(row.get("invariant_id", "")))
        ],
    }


def _assert_required_checks(event_row: dict) -> str:
    checks = [dict(item) for item in list(event_row.get("invariant_checks") or []) if isinstance(item, dict)]
    by_id = dict((str(item.get("invariant_id", "")), str(item.get("status", ""))) for item in checks)
    for invariant_id in REQUIRED_INVARIANT_IDS:
        status = str(by_id.get(invariant_id, "")).strip()
        if not status:
            return "missing required transition invariant check '{}'".format(invariant_id)
        if status == "fail":
            return "required transition invariant check '{}' failed".format(invariant_id)
    if not str(event_row.get("deterministic_fingerprint", "")).strip():
        return "transition event missing deterministic_fingerprint"
    return ""


def _run_sequence() -> tuple:
    from tools.xstack.testx.tests.lod_invariance_testlib import base_state, execute_region_transition

    state = copy.deepcopy(base_state())
    expanded = execute_region_transition(
        state=state,
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
    )
    if str(expanded.get("result", "")) != "complete":
        return (), "region expand refused unexpectedly"
    collapsed = execute_region_transition(
        state=state,
        process_id="process.region_collapse",
        strict_contracts=True,
        memory_enabled=False,
    )
    if str(collapsed.get("result", "")) != "complete":
        return (), "region collapse refused unexpectedly"

    expand_events = [dict(item) for item in list(expanded.get("transition_events") or []) if isinstance(item, dict)]
    collapse_events = [dict(item) for item in list(collapsed.get("transition_events") or []) if isinstance(item, dict)]
    if len(expand_events) != 1 or len(collapse_events) != 1:
        return (), "expected one transition event for expand and collapse"

    expand_error = _assert_required_checks(expand_events[0])
    if expand_error:
        return (), expand_error
    collapse_error = _assert_required_checks(collapse_events[0])
    if collapse_error:
        return (), collapse_error

    return (
        _event_summary(expand_events[0]),
        _event_summary(collapse_events[0]),
    ), ""


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first, first_error = _run_sequence()
    if first_error:
        return {"status": "fail", "message": first_error}
    second, second_error = _run_sequence()
    if second_error:
        return {"status": "fail", "message": second_error}
    if tuple(first) != tuple(second):
        return {"status": "fail", "message": "transition invariant summaries diverged across repeated runs"}

    return {"status": "pass", "message": "expand/collapse transition invariant checks are deterministic"}
