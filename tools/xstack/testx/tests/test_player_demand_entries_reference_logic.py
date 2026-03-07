"""FAST test: LOGIC-gated player demand entries explicitly reference the LOGIC series."""

from __future__ import annotations


TEST_ID = "test_player_demand_entries_reference_logic"
TEST_TAGS = ["fast", "logic", "genre", "matrix"]


_REQUIRED_DEMANDS = {
    "fact.plc_control_panel": "LOGIC-2",
    "fact.automated_factory": "LOGIC-2",
    "trans.train_interlocking_cabinet": "LOGIC-2",
    "space.reactor_control_room": "LOGIC-2",
    "city.smart_power_grid": "LOGIC-3",
    "cyber.hacking_scada": "LOGIC-3",
    "mil.drone_autopilot": "LOGIC-3",
    "city.traffic_lights_coordination": "LOGIC-3",
    "cyber.firmware_flashing_pipeline_integration": "LOGIC-2",
}


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_genre0_testlib

    payload, err = meta_genre0_testlib.load_matrix(repo_root)
    if err:
        return {"status": "fail", "message": "matrix payload missing or invalid"}

    by_id = {
        str(row.get("demand_id", "")).strip(): dict(row)
        for row in meta_genre0_testlib.matrix_demands(payload)
        if str(row.get("demand_id", "")).strip()
    }
    for demand_id, expected_series in _REQUIRED_DEMANDS.items():
        row = dict(by_id.get(demand_id) or {})
        if not row:
            return {"status": "fail", "message": "missing player demand row {}".format(demand_id)}
        if str(row.get("next_series", "")).strip() != expected_series:
            return {"status": "fail", "message": "{} must point to {}".format(demand_id, expected_series)}
        if not bool((dict(row.get("sig_logic") or {})).get("needs", False)):
            return {"status": "fail", "message": "{} must declare sig_logic.needs=true".format(demand_id)}
        notes = str(row.get("notes", "")).strip()
        if "LOGIC" not in notes:
            return {"status": "fail", "message": "{} notes must mention LOGIC dependency".format(demand_id)}
    return {"status": "pass", "message": "LOGIC-gated player demands reference the LOGIC series"}
