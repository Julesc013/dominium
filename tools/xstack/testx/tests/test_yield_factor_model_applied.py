"""FAST test: CHEM-2 process run yield factor comes from model evaluation inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_yield_factor_model_applied"
TEST_TAGS = ["fast", "chem", "yield", "model"]


def _run_with_catalyst(repo_root: str, catalyst_present: bool) -> dict:
    from tools.xstack.testx.tests.chem_testlib import execute_process_run_lifecycle, seed_process_run_state

    state = seed_process_run_state()
    lifecycle = execute_process_run_lifecycle(
        repo_root=repo_root,
        state=state,
        catalyst_present=bool(catalyst_present),
        spec_score_permille=920,
        temperature=640,
        pressure_head=180,
    )
    return {"state": dict(state), "lifecycle": dict(lifecycle)}


def _latest_yield_factor(state: dict, run_id: str) -> int:
    run_rows = [dict(row) for row in list(state.get("chem_process_run_state_rows") or []) if isinstance(row, dict)]
    for row in run_rows:
        if str(row.get("run_id", "")).strip() != str(run_id).strip():
            continue
        ext = dict(row.get("extensions") or {})
        return int(max(0, int(ext.get("last_yield_factor_permille", 0) or 0)))
    return 0


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    base = _run_with_catalyst(repo_root, catalyst_present=False)
    boosted = _run_with_catalyst(repo_root, catalyst_present=True)

    for label, payload in (("base", base), ("boosted", boosted)):
        tick_result = str((dict(payload.get("lifecycle") or {}).get("tick", {}) or {}).get("result", "")).strip()
        if tick_result != "complete":
            return {"status": "fail", "message": "{} process_run_tick failed".format(label)}

    run_id = str((dict(base.get("lifecycle") or {})).get("run_id", "")).strip()
    base_factor = _latest_yield_factor(dict(base.get("state") or {}), run_id)
    boosted_factor = _latest_yield_factor(dict(boosted.get("state") or {}), run_id)
    if base_factor <= 0 or boosted_factor <= 0:
        return {"status": "fail", "message": "missing model-driven yield_factor in process run state extensions"}
    if boosted_factor < base_factor:
        return {
            "status": "fail",
            "message": "catalyst-on run yielded lower factor ({} < {})".format(boosted_factor, base_factor),
        }

    yield_rows = [dict(row) for row in list(dict(boosted.get("state") or {}).get("chem_yield_model_rows") or []) if isinstance(row, dict)]
    if not yield_rows:
        return {"status": "fail", "message": "missing chem_yield_model_rows after process_run_tick"}
    if not str(yield_rows[-1].get("yield_model_id", "")).strip():
        return {"status": "fail", "message": "yield model row missing yield_model_id"}
    return {"status": "pass", "message": "CHEM-2 yield factor is model-driven and catalyst-sensitive"}
