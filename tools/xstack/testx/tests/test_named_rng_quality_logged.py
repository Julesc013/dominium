"""FAST test: PROC-2 optional named RNG quality path emits deterministic RNG logs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_named_rng_quality_logged"
TEST_TAGS = ["fast", "proc", "quality", "rng"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc2_testlib import run_proc2_quality_case

    payload = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.rng.quality",
        yield_model_id="yield.named_rng_optional",
        defect_model_id="defect.named_rng_optional",
        stochastic_quality_enabled=True,
    )
    if str((dict(payload.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_end failed"}
    state = dict(payload.get("state") or {})
    rng_rows = [dict(row) for row in list(state.get("quality_rng_event_rows") or []) if isinstance(row, dict)]
    if not rng_rows:
        return {"status": "fail", "message": "missing quality_rng_event_rows for named RNG path"}
    for row in rng_rows:
        rng_name = str(row.get("rng_stream_name", "")).strip()
        seed_hash = str(row.get("rng_seed_hash", "")).strip().lower()
        if not rng_name:
            return {"status": "fail", "message": "rng row missing rng_stream_name"}
        if not _HASH64.fullmatch(seed_hash):
            return {"status": "fail", "message": "rng row missing deterministic rng_seed_hash"}
    return {"status": "pass", "message": "PROC-2 named RNG quality path is logged deterministically"}
