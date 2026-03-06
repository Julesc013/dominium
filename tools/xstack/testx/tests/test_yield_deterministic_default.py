"""FAST test: PROC-2 default yield model is deterministic for equivalent runs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_yield_deterministic_default"
TEST_TAGS = ["fast", "proc", "quality", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc2_testlib import run_proc2_quality_case

    first = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.det.yield",
        yield_model_id="yield.default_deterministic",
        defect_model_id="defect.default_deterministic",
    )
    second = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.det.yield",
        yield_model_id="yield.default_deterministic",
        defect_model_id="defect.default_deterministic",
    )

    for label, payload in (("first", first), ("second", second)):
        if str((dict(payload.get("end") or {})).get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "{} process_run_end failed".format(label)}
        state = dict(payload.get("state") or {})
        chain = str(state.get("process_quality_hash_chain", "")).strip().lower()
        if not _HASH64.fullmatch(chain):
            return {"status": "fail", "message": "{} missing process_quality_hash_chain".format(label)}

    a_state = dict(first.get("state") or {})
    b_state = dict(second.get("state") or {})
    if str(a_state.get("process_quality_hash_chain", "")).strip().lower() != str(b_state.get("process_quality_hash_chain", "")).strip().lower():
        return {"status": "fail", "message": "process quality hash chain drifted across equivalent runs"}

    rows = [dict(row) for row in list(a_state.get("process_quality_record_rows") or []) if isinstance(row, dict)]
    if not rows:
        return {"status": "fail", "message": "missing process_quality_record_rows"}
    yield_factor = int(rows[-1].get("yield_factor", 0) or 0)
    if yield_factor <= 0:
        return {"status": "fail", "message": "invalid deterministic yield_factor"}
    return {"status": "pass", "message": "PROC-2 default yield model deterministic"}
