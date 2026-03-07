"""FAST test: LOGIC-1 signal mutation flows through canonical processes."""

from __future__ import annotations

import json
import os


TEST_ID = "test_signal_set_process_only"
TEST_TAGS = ["fast", "logic", "process"]


def run(repo_root: str):
    from src.logic.signal import process_signal_set

    process_registry_path = os.path.join(repo_root, "data/registries/process_registry.json".replace("/", os.sep))
    runtime_path = os.path.join(repo_root, "tools/xstack/sessionx/process_runtime.py".replace("/", os.sep))
    payload = json.load(open(process_registry_path, "r", encoding="utf-8"))
    process_rows = list(payload.get("processes") or payload.get("record", {}).get("processes") or payload.get("records") or [])
    process_ids = {str(row.get("process_id", "")).strip() for row in process_rows if isinstance(row, dict)}
    for process_id in ("process.signal_set", "process.signal_emit_pulse"):
        if process_id not in process_ids:
            return {"status": "fail", "message": "missing canonical signal process '{}'".format(process_id)}
    runtime_text = open(runtime_path, "r", encoding="utf-8").read()
    for token in ('elif process_id == "process.signal_set":', 'elif process_id == "process.signal_emit_pulse":'):
        if token not in runtime_text:
            return {"status": "fail", "message": "runtime missing dispatch token '{}'".format(token)}
    out = process_signal_set(
        current_tick=3,
        signal_store_state=None,
        signal_request={
            "network_id": "net.logic",
            "element_id": "elem.logic",
            "port_id": "port.out",
            "signal_type_id": "signal.boolean",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value": 1},
        },
        signal_type_registry_payload={"record": {"signal_types": [{"signal_type_id": "signal.boolean"}]}},
        carrier_type_registry_payload={"record": {"carrier_types": [{"carrier_type_id": "carrier.electrical"}]}},
        signal_delay_policy_registry_payload={"record": {"signal_delay_policies": [{"delay_policy_id": "delay.none"}]}},
        signal_noise_policy_registry_payload={"record": {"signal_noise_policies": [{"noise_policy_id": "noise.none"}]}},
    )
    if str(out.get("result", "")) != "complete":
        return {"status": "fail", "message": "process_signal_set did not complete"}
    change_rows = list(out.get("signal_change_record_rows") or [])
    if not change_rows or str(change_rows[0].get("process_id", "")).strip() != "process.signal_set":
        return {"status": "fail", "message": "signal mutation did not record canonical process id"}
    return {"status": "pass", "message": "signal mutation constrained to canonical processes"}
