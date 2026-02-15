"""FAST test: session stage/pipeline registries declare multiplayer net stages."""

from __future__ import annotations

import json
import os


TEST_ID = "testx.net.pipeline_has_net_stages"
TEST_TAGS = ["smoke", "session", "net"]


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    stage_path = os.path.join(repo_root, "data", "registries", "session_stage_registry.json")
    pipeline_path = os.path.join(repo_root, "data", "registries", "session_pipeline_registry.json")
    try:
        stage_payload = _read_json(stage_path)
        pipeline_payload = _read_json(pipeline_path)
    except (OSError, ValueError):
        return {"status": "fail", "message": "session pipeline registry files missing or invalid"}

    stage_rows = (((stage_payload.get("record") or {}).get("stages")) or [])
    if not isinstance(stage_rows, list):
        return {"status": "fail", "message": "session stage registry stages list missing"}
    stage_map = {}
    for row in stage_rows:
        if isinstance(row, dict):
            stage_map[str(row.get("stage_id", "")).strip()] = row

    required_stage_ids = [
        "stage.net_handshake",
        "stage.net_sync_baseline",
        "stage.net_join_world",
    ]
    for stage_id in required_stage_ids:
        if stage_id not in stage_map:
            return {"status": "fail", "message": "missing session stage '{}'".format(stage_id)}

    verify_stage = dict(stage_map.get("stage.verify_world") or {})
    allowed_next = set(str(item).strip() for item in (verify_stage.get("allowed_next_stage_ids") or []))
    if "stage.net_handshake" not in allowed_next:
        return {"status": "fail", "message": "stage.verify_world must allow stage.net_handshake"}

    pipeline_rows = (((pipeline_payload.get("record") or {}).get("pipelines")) or [])
    if not isinstance(pipeline_rows, list):
        return {"status": "fail", "message": "session pipeline registry pipelines list missing"}
    selected = {}
    for row in pipeline_rows:
        if isinstance(row, dict) and str(row.get("pipeline_id", "")).strip() == "pipeline.client.multiplayer_stub":
            selected = row
            break
    if not selected:
        return {"status": "fail", "message": "pipeline.client.multiplayer_stub is missing"}

    stages = [str(item).strip() for item in (selected.get("stages") or []) if str(item).strip()]
    expected_chain = ["stage.net_handshake", "stage.net_sync_baseline", "stage.net_join_world"]
    positions = []
    for stage_id in expected_chain:
        if stage_id not in stages:
            return {"status": "fail", "message": "pipeline.client.multiplayer_stub missing '{}'".format(stage_id)}
        positions.append(stages.index(stage_id))
    if positions != sorted(positions):
        return {"status": "fail", "message": "multiplayer net stages must be ordered deterministically"}

    return {"status": "pass", "message": "session stage and pipeline registries include multiplayer net stages"}
