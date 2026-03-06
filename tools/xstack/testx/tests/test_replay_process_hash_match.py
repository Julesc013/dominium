"""FAST test: PROC replay tool returns stable hash matches for equivalent payloads."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_process_hash_match"
TEST_TAGS = ["fast", "proc", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.process.tool_replay_process_window import verify_process_replay_window

    state = {
        "process_run_record_rows": [
            {
                "run_id": "process_run.test",
                "process_id": "proc.test.replay",
                "version": "1.0.0",
                "start_tick": 10,
                "end_tick": 12,
                "status": "completed",
            }
        ],
        "process_step_record_rows": [
            {"run_id": "process_run.test", "step_id": "step.a", "tick": 10, "status": "started"},
            {"run_id": "process_run.test", "step_id": "step.a", "tick": 11, "status": "completed"},
        ],
    }
    first = verify_process_replay_window(state_payload=state)
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "initial replay verification failed"}

    baseline = dict(state)
    baseline["process_run_record_hash_chain"] = str((first.get("observed") or {}).get("process_run_record_hash_chain", "")).strip()
    baseline["process_step_record_hash_chain"] = str((first.get("observed") or {}).get("process_step_record_hash_chain", "")).strip()

    second = verify_process_replay_window(state_payload=baseline, expected_payload=baseline)
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "replay verification with baseline failed"}

    for key in ("process_run_record_hash_chain", "process_step_record_hash_chain"):
        observed = str((second.get("observed") or {}).get(key, "")).strip()
        expected = str((second.get("expected") or {}).get(key, "")).strip()
        if (not observed) or (observed != expected):
            return {"status": "fail", "message": "hash mismatch for {}".format(key)}

    return {"status": "pass", "message": "process replay hashes are stable"}
