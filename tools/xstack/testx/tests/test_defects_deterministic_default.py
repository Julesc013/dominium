"""FAST test: PROC-2 default defect outcomes are deterministic for equivalent runs."""

from __future__ import annotations

import sys


TEST_ID = "test_defects_deterministic_default"
TEST_TAGS = ["fast", "proc", "quality", "defect"]


def _defect_snapshot(state: dict) -> tuple[tuple[str, ...], int]:
    rows = [dict(row) for row in list(state.get("process_quality_record_rows") or []) if isinstance(row, dict)]
    if not rows:
        return tuple(), 0
    row = dict(rows[-1])
    return tuple(sorted(set(str(flag).strip() for flag in list(row.get("defect_flags") or []) if str(flag).strip()))), int(row.get("yield_factor", 0) or 0)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc2_testlib import run_proc2_quality_case

    quality_inputs = {
        "temperature": 980,
        "pressure_head": 980,
        "entropy_index": 900,
        "tool_wear_permille": 990,
        "input_batch_quality_permille": 640,
        "spec_score_permille": 620,
        "calibration_state_permille": 600,
    }
    first = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.det.defect",
        yield_model_id="yield.default_deterministic",
        defect_model_id="defect.default_deterministic",
        quality_inputs=quality_inputs,
    )
    second = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.det.defect",
        yield_model_id="yield.default_deterministic",
        defect_model_id="defect.default_deterministic",
        quality_inputs=quality_inputs,
    )
    for label, payload in (("first", first), ("second", second)):
        if str((dict(payload.get("end") or {})).get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "{} process_run_end failed".format(label)}
    flags_a, yield_a = _defect_snapshot(dict(first.get("state") or {}))
    flags_b, yield_b = _defect_snapshot(dict(second.get("state") or {}))
    if flags_a != flags_b or yield_a != yield_b:
        return {"status": "fail", "message": "defect/yield outcomes drifted across equivalent runs"}
    if not flags_a:
        return {"status": "fail", "message": "expected deterministic defect flags for stressed input case"}
    return {"status": "pass", "message": "PROC-2 default defect outcomes are deterministic"}
