"""FAST test: SYS0 collapse includes deterministic boundary invariant checks."""

from __future__ import annotations

import sys


TEST_ID = "test_boundary_invariant_preserved_after_collapse"
TEST_TAGS = ["fast", "system", "sys0", "invariants"]


_REQUIRED = {
    "invariant.mass_conserved",
    "invariant.energy_conserved",
    "invariant.pollutant_accounted",
}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys0_testlib import cloned_state, execute_system_process

    state = cloned_state()
    result = execute_system_process(
        state=state,
        process_id="process.system_collapse",
        inputs={"system_id": "system.engine.alpha"},
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "system collapse refused unexpectedly for invariant check"}

    checks = [dict(row) for row in list(result.get("invariant_checks") or []) if isinstance(row, dict)]
    if not checks:
        return {"status": "fail", "message": "collapse did not emit boundary invariant checks"}

    seen = set(str(row.get("invariant_id", "")).strip() for row in checks)
    if not _REQUIRED.issubset(seen):
        return {"status": "fail", "message": "collapse invariant checks missing required ids"}
    for row in checks:
        if str(row.get("invariant_id", "")).strip() in _REQUIRED and str(row.get("status", "")).strip() != "pass":
            return {"status": "fail", "message": "required boundary invariant check failed"}

    return {"status": "pass", "message": "boundary invariant checks preserved on collapse"}
