"""FAST test: the frozen MVP logic interaction remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_logic_compile_deterministic"
TEST_TAGS = ["fast", "omega", "gameplay", "logic"]

LOGIC_FIELDS = (
    "compiled_model_hash",
    "toggle_off_final_signal_hash",
    "toggle_on_final_signal_hash",
    "logic_debug_request_hash_chain",
    "logic_debug_trace_hash_chain",
    "logic_protocol_summary_hash_chain",
)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.gameplay_loop_common import load_gameplay_snapshot
    from tools.mvp.mvp_smoke_common import run_logic_smoke_suite

    snapshot = load_gameplay_snapshot(repo_root)
    expected_logic = dict(dict(snapshot.get("record") or {}).get("logic") or {})
    first = dict(run_logic_smoke_suite(repo_root) or {})
    second = dict(run_logic_smoke_suite(repo_root) or {})
    if first != second:
        return {"status": "fail", "message": "logic smoke suite diverged across repeated runs"}
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "logic smoke suite did not complete"}
    for field in LOGIC_FIELDS:
        if str(first.get(field, "")).strip() != str(expected_logic.get(field, "")).strip():
            return {"status": "fail", "message": "logic smoke hash mismatch for {}".format(field)}
    return {"status": "pass", "message": "MVP logic interaction remains deterministic"}
