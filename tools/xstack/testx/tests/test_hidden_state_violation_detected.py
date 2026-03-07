"""FAST test: STATEVEC0 detects undeclared output-affecting fields and refuses collapse in debug guard mode."""

from __future__ import annotations

import sys


TEST_ID = "test_hidden_state_violation_detected"
TEST_TAGS = ["fast", "statevec", "enforcement", "hidden_state"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.system.statevec import detect_undeclared_output_state
    from tools.xstack.testx.tests.sys0_testlib import cloned_state, execute_system_process

    state = cloned_state()
    state["profile_registry_payload"] = {
        "profiles": [
            {
                "profile_id": "law.test_statevec_guard",
                "profile_type": "law",
                "version": "1.0.0",
                "overrides": {"rule.statevec.output_guard": True},
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ]
    }
    state["profile_binding_rows"] = [
        {
            "binding_id": "binding.test.statevec_guard",
            "scope": "session",
            "target_id": "*",
            "profile_id": "law.test_statevec_guard",
            "tick_applied": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    system_rows = [dict(row) for row in list(state.get("system_rows") or []) if isinstance(row, dict)]
    if not system_rows:
        return {"status": "fail", "message": "missing system rows in fixture"}
    system = dict(system_rows[0])
    ext = dict(system.get("extensions") or {})
    ext["output_affecting_state_fields"] = ["hysteresis_flag"]
    system["extensions"] = ext
    state["system_rows"] = [system]

    direct_check = detect_undeclared_output_state(
        owner_id="system.system.engine.alpha",
        output_affecting_fields=["hysteresis_flag"],
        state_vector_definition_rows=state.get("state_vector_definition_rows") or [],
    )
    if not bool(direct_check.get("violation", False)):
        return {"status": "fail", "message": "direct undeclared-output-state check did not detect violation"}

    result = execute_system_process(
        state=state,
        process_id="process.system_collapse",
        inputs={"system_id": "system.engine.alpha"},
    )
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "collapse should refuse when debug statevec guard trips"}

    refusal = dict(result.get("refusal") or {})
    details = dict(refusal.get("details") or refusal.get("relevant_ids") or {})
    statevec_reason = str(details.get("statevec_reason_code", "")).strip()
    if statevec_reason != "refusal.statevec.undeclared_output_field":
        return {
            "status": "fail",
            "message": "unexpected statevec reason code: {}".format(statevec_reason or "missing"),
        }

    violation_rows = [dict(row) for row in list(state.get("state_vector_violation_rows") or []) if isinstance(row, dict)]
    if not violation_rows:
        return {"status": "fail", "message": "state vector violation row was not logged"}

    return {"status": "pass", "message": "undeclared output state violation is detected and logged"}
