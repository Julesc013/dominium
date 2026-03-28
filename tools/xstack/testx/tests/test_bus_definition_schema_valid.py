"""FAST test: LOGIC-1 bus schema and registry baseline are present."""

from __future__ import annotations

import json
import os


TEST_ID = "test_bus_definition_schema_valid"
TEST_TAGS = ["fast", "logic", "schema", "bus"]


def run(repo_root: str):
    from logic.signal import build_bus_definition_row

    schema_path = os.path.join(repo_root, "schema/logic/bus_definition.schema".replace("/", os.sep))
    registry_path = os.path.join(repo_root, "data/registries/bus_encoding_registry.json".replace("/", os.sep))
    if not os.path.isfile(schema_path):
        return {"status": "fail", "message": "bus definition schema missing"}
    if not os.path.isfile(registry_path):
        return {"status": "fail", "message": "bus encoding registry missing"}
    text = open(schema_path, "r", encoding="utf-8").read()
    for token in ("bus_id", "encoding_id", "width", "fields", "deterministic_fingerprint"):
        if token not in text:
            return {"status": "fail", "message": "bus definition schema missing token '{}'".format(token)}
    payload = json.load(open(registry_path, "r", encoding="utf-8"))
    rows = list((dict(payload.get("record") or {})).get("bus_encodings") or [])
    encoding_ids = {str(row.get("encoding_id", "")).strip() for row in rows if isinstance(row, dict)}
    if {"encoding.bits", "encoding.uint", "encoding.struct", "encoding.frame"} - encoding_ids:
        return {"status": "fail", "message": "bus encoding registry missing required encoding ids"}
    built = build_bus_definition_row(
        bus_id="bus.logic.test",
        encoding_id="encoding.struct",
        width=8,
        fields=[{"field_id": "bit0", "signal_type_id": "signal.boolean"}],
    )
    if not built or str(built.get("bus_id", "")).strip() != "bus.logic.test":
        return {"status": "fail", "message": "bus definition builder failed to normalize payload"}
    return {"status": "pass", "message": "bus schema and registry baseline valid"}
