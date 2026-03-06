"""FAST test: PROC-2 output batch quality rows include required traceability links."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_batch_quality_traceability_links"
TEST_TAGS = ["fast", "proc", "quality", "traceability"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc2_testlib import run_proc2_quality_case

    payload = run_proc2_quality_case(
        repo_root=repo_root,
        run_id="run.proc2.traceability",
        yield_model_id="yield.default_deterministic",
        defect_model_id="defect.default_deterministic",
    )
    if str((dict(payload.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_end failed"}
    state = dict(payload.get("state") or {})
    rows = [dict(row) for row in list(state.get("batch_quality_rows") or []) if isinstance(row, dict)]
    if not rows:
        return {"status": "fail", "message": "missing output batch_quality rows"}
    for row in rows:
        traceability = dict((dict(row.get("extensions") or {})).get("traceability") or {})
        if not str(traceability.get("run_id", "")).strip():
            return {"status": "fail", "message": "traceability.run_id missing"}
        if not str(traceability.get("process_id", "")).strip():
            return {"status": "fail", "message": "traceability.process_id missing"}
        if not str(traceability.get("process_version", "")).strip():
            return {"status": "fail", "message": "traceability.process_version missing"}
        if not list(traceability.get("input_batch_ids") or []):
            return {"status": "fail", "message": "traceability.input_batch_ids missing"}
        if not list(traceability.get("tool_ids") or []):
            return {"status": "fail", "message": "traceability.tool_ids missing"}
        env_hash = str(traceability.get("environment_snapshot_hash", "")).strip().lower()
        if not _HASH64.fullmatch(env_hash):
            return {"status": "fail", "message": "traceability.environment_snapshot_hash missing/invalid"}
    return {"status": "pass", "message": "PROC-2 batch quality traceability links are present"}
