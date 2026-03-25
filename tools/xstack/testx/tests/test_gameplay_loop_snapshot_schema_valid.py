"""FAST test: MVP gameplay loop snapshot structure and fingerprint are valid."""

from __future__ import annotations

import sys


TEST_ID = "test_gameplay_loop_snapshot_schema_valid"
TEST_TAGS = ["fast", "omega", "gameplay", "schema"]

EXPECTED_STEP_IDS = [
    "STEP_1",
    "STEP_2",
    "STEP_3",
    "STEP_4",
    "STEP_5",
    "STEP_6",
    "STEP_7",
    "STEP_8",
]
EXPECTED_CHECKPOINT_IDS = ["T0", "T1", "T2", "T3"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.gameplay_loop_common import MVP_GAMEPLAY_SCHEMA_ID, gameplay_snapshot_record_hash, load_gameplay_snapshot

    payload = load_gameplay_snapshot(repo_root)
    record = dict(payload.get("record") or {})
    if str(payload.get("schema_id", "")).strip() != MVP_GAMEPLAY_SCHEMA_ID:
        return {"status": "fail", "message": "MVP gameplay loop snapshot schema_id mismatch"}
    if str(payload.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "MVP gameplay loop snapshot schema_version mismatch"}
    try:
        gameplay_loop_version = int(record.get("gameplay_loop_version", -1))
    except (TypeError, ValueError):
        gameplay_loop_version = -1
    if gameplay_loop_version != 0:
        return {"status": "fail", "message": "MVP gameplay loop version mismatch"}
    if str(record.get("stability_class", "")).strip() != "stable":
        return {"status": "fail", "message": "MVP gameplay loop stability_class mismatch"}
    if not str(dict(record.get("launch") or {}).get("command", "")).strip():
        return {"status": "fail", "message": "MVP gameplay loop launch command missing"}
    step_ids = [str(item.get("step_id", "")).strip() for item in list(record.get("steps") or []) if isinstance(item, dict)]
    if step_ids != EXPECTED_STEP_IDS:
        return {"status": "fail", "message": "MVP gameplay loop step order mismatch"}
    checkpoint_ids = [str(item.get("checkpoint_id", "")).strip() for item in list(record.get("proof_anchors") or []) if isinstance(item, dict)]
    if checkpoint_ids != EXPECTED_CHECKPOINT_IDS:
        return {"status": "fail", "message": "MVP gameplay loop proof anchor schedule mismatch"}
    replay = dict(record.get("replay") or {})
    if not str(replay.get("replay_t3_state_hash_anchor", "")).strip():
        return {"status": "fail", "message": "MVP gameplay loop replay final anchor missing"}
    fingerprint = str(record.get("deterministic_fingerprint", "")).strip()
    if fingerprint != gameplay_snapshot_record_hash(record):
        return {"status": "fail", "message": "MVP gameplay loop snapshot deterministic_fingerprint mismatch"}
    return {"status": "pass", "message": "MVP gameplay loop snapshot structure valid"}
