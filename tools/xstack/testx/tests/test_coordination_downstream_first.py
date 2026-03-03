"""FAST test: downstream-first co-ordination orders electrical trip actions deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_coordination_downstream_first"
TEST_TAGS = ["fast", "electric", "protection", "coordination"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.electric.protection.protection_engine import evaluate_protection_trip_plan

    fault_rows = [
        {
            "schema_version": "1.0.0",
            "fault_id": "fault.elec.coord.test",
            "fault_kind_id": "fault.overcurrent",
            "target_kind": "edge",
            "target_id": "edge.elec.coord",
            "detected_tick": 7,
            "severity": 4000,
            "active": True,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    protection_device_rows = [
        {
            "schema_version": "1.0.0",
            "device_id": "device.elec.upstream",
            "device_kind_id": "breaker",
            "attached_to": {"edge_id": "edge.elec.coord"},
            "state_machine_id": "machine.elec.upstream",
            "spec_id": None,
            "settings_ref": "settings.elec.upstream",
            "deterministic_fingerprint": "",
            "extensions": {"channel_id": "channel.elec.coord", "downstream_rank": 10},
        },
        {
            "schema_version": "1.0.0",
            "device_id": "device.elec.downstream",
            "device_kind_id": "breaker",
            "attached_to": {"edge_id": "edge.elec.coord"},
            "state_machine_id": "machine.elec.downstream",
            "spec_id": None,
            "settings_ref": "settings.elec.downstream",
            "deterministic_fingerprint": "",
            "extensions": {"channel_id": "channel.elec.coord", "downstream_rank": 1},
        },
    ]
    protection_settings_rows = [
        {
            "schema_version": "1.0.0",
            "settings_id": "settings.elec.upstream",
            "trip_threshold_P": None,
            "trip_threshold_S": 1,
            "trip_delay_ticks": 0,
            "gfci_threshold": None,
            "coordination_group_id": "coord.group.main",
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "settings_id": "settings.elec.downstream",
            "trip_threshold_P": None,
            "trip_threshold_S": 1,
            "trip_delay_ticks": 0,
            "gfci_threshold": None,
            "coordination_group_id": "coord.group.main",
            "deterministic_fingerprint": "",
            "extensions": {},
        },
    ]
    result = evaluate_protection_trip_plan(
        fault_rows=fault_rows,
        protection_device_rows=protection_device_rows,
        protection_settings_rows=protection_settings_rows,
        current_tick=8,
        coordination_policy_id="coord.downstream_first",
        max_trip_actions=2,
    )
    trip_rows = [dict(row) for row in list(result.get("trip_rows") or []) if isinstance(row, dict)]
    if len(trip_rows) < 2:
        return {"status": "fail", "message": "expected both downstream and upstream devices to be scheduled for trip"}
    if str(trip_rows[0].get("device_id", "")).strip() != "device.elec.downstream":
        return {"status": "fail", "message": "downstream-first policy must order downstream device before upstream"}
    if str(trip_rows[1].get("device_id", "")).strip() != "device.elec.upstream":
        return {"status": "fail", "message": "upstream device ordering mismatch under downstream-first policy"}
    return {"status": "pass", "message": "downstream-first trip coordination deterministic"}

