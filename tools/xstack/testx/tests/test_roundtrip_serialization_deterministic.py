"""FAST test: STATEVEC0 serialize/deserialize roundtrip is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_roundtrip_serialization_deterministic"
TEST_TAGS = ["fast", "statevec", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.system.statevec import deserialize_state, serialize_state
    from tools.xstack.testx.tests.statevec0_testlib import (
        source_state_payload,
        state_vector_definition_rows,
    )

    owner_id = "system.system.engine.alpha"
    definitions = state_vector_definition_rows(owner_id=owner_id)
    payload_a = source_state_payload()
    payload_b = copy.deepcopy(payload_a)
    payload_b["root_assembly_id"] = payload_a["root_assembly_id"]
    payload_b["captured_tick"] = payload_a["captured_tick"]

    first = serialize_state(
        owner_id=owner_id,
        source_state=payload_a,
        state_vector_definition_rows=definitions,
        current_tick=11,
        expected_version="1.0.0",
    )
    second = serialize_state(
        owner_id=owner_id,
        source_state=payload_b,
        state_vector_definition_rows=definitions,
        current_tick=11,
        expected_version="1.0.0",
    )
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "serialize_state failed"}
    if str(first.get("anchor_hash", "")).strip() != str(second.get("anchor_hash", "")).strip():
        return {"status": "fail", "message": "anchor hash drift across equivalent inputs"}

    restored = deserialize_state(
        snapshot_row=dict(first.get("snapshot_row") or {}),
        state_vector_definition_rows=definitions,
        expected_version="1.0.0",
    )
    if str(restored.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "deserialize_state failed"}

    replay = serialize_state(
        owner_id=owner_id,
        source_state=dict(restored.get("restored_state") or {}),
        state_vector_definition_rows=definitions,
        current_tick=11,
        expected_version="1.0.0",
    )
    if str(replay.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "replay serialize_state failed"}
    if str(first.get("anchor_hash", "")).strip() != str(replay.get("anchor_hash", "")).strip():
        return {"status": "fail", "message": "roundtrip anchor mismatch"}

    return {"status": "pass", "message": "state vector roundtrip is deterministic"}
