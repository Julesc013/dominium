"""FAST test: THERM-2 heat exchanger interface stub is registered for FLUID coupling."""

from __future__ import annotations

import json
import os


TEST_ID = "test_heat_exchanger_stub_exists"
TEST_TAGS = ["fast", "thermal", "interface", "registry"]


def _load_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _row_by_id(rows: object, key_field: str, key_value: str) -> dict:
    for row in list(rows or []):
        if not isinstance(row, dict):
            continue
        if str(row.get(key_field, "")).strip() == key_value:
            return dict(row)
    return {}


def run(repo_root: str):
    machine_path = os.path.join(repo_root, "data", "registries", "machine_type_registry.json")
    port_path = os.path.join(repo_root, "data", "registries", "port_type_registry.json")
    if not os.path.isfile(machine_path):
        return {"status": "fail", "message": "machine_type_registry.json missing"}
    if not os.path.isfile(port_path):
        return {"status": "fail", "message": "port_type_registry.json missing"}

    machine_payload = _load_json(machine_path)
    port_payload = _load_json(port_path)
    machine_rows = list(dict(machine_payload.get("record") or {}).get("machine_types") or [])
    port_rows = list(dict(port_payload.get("record") or {}).get("port_types") or [])

    machine_row = _row_by_id(machine_rows, "machine_type_id", "machine.heat_exchanger.stub")
    if not machine_row:
        return {"status": "fail", "message": "missing machine.heat_exchanger.stub in machine_type_registry"}

    required_ports = set(str(token).strip() for token in list(machine_row.get("required_ports") or []))
    expected_ports = {"port.thermal_in", "port.thermal_out", "port.fluid_in_stub", "port.fluid_out_stub"}
    if not expected_ports.issubset(required_ports):
        return {"status": "fail", "message": "heat exchanger stub missing required thermal/fluid ports"}

    machine_ext = dict(machine_row.get("extensions") or {})
    if str(machine_ext.get("spec_template_id", "")).strip() != "spec.heat_exchanger":
        return {"status": "fail", "message": "heat exchanger stub missing spec.heat_exchanger linkage"}

    missing_ports = []
    for port_id in sorted(expected_ports):
        if not _row_by_id(port_rows, "port_type_id", port_id):
            missing_ports.append(port_id)
    if missing_ports:
        return {"status": "fail", "message": "missing port type entries: {}".format(",".join(missing_ports))}
    return {"status": "pass", "message": "heat exchanger stub interface registry entries present"}

