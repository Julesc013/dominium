"""FAST test: LOGIC policy registry declares constitutional loop and compute controls."""

from __future__ import annotations

import json
import os


TEST_ID = "test_logic_policy_declared"
TEST_TAGS = ["fast", "logic", "policy"]


def _load(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid"


def run(repo_root: str):
    logic_payload, logic_err = _load(repo_root, "data/registries/logic_policy_registry.json")
    compute_payload, compute_err = _load(repo_root, "data/registries/compute_budget_profile_registry.json")
    if logic_err:
        return {"status": "fail", "message": "logic policy registry missing or invalid"}
    if compute_err:
        return {"status": "fail", "message": "compute budget profile registry missing or invalid"}

    logic_rows = list((dict(logic_payload.get("record") or {})).get("logic_policies") or [])
    compute_rows = list((dict(compute_payload.get("record") or {})).get("compute_budget_profiles") or [])
    known_compute_ids = {
        str(row.get("compute_profile_id", "")).strip()
        for row in compute_rows
        if isinstance(row, dict) and str(row.get("compute_profile_id", "")).strip()
    }
    by_id = {
        str(row.get("policy_id", "")).strip(): dict(row)
        for row in logic_rows
        if isinstance(row, dict) and str(row.get("policy_id", "")).strip()
    }

    for policy_id in ("logic.default", "logic.rank_strict", "logic.lab_experimental"):
        row = dict(by_id.get(policy_id) or {})
        if not row:
            return {"status": "fail", "message": "missing logic policy {}".format(policy_id)}
        compute_profile_id = str(row.get("compute_profile_id", "")).strip()
        if compute_profile_id not in known_compute_ids:
            return {
                "status": "fail",
                "message": "{} references unknown compute profile {}".format(policy_id, compute_profile_id or "<missing>"),
            }

    if bool(by_id["logic.default"].get("allow_combinational_loops", False)):
        return {"status": "fail", "message": "logic.default must refuse combinational loops"}
    if bool(by_id["logic.rank_strict"].get("allow_combinational_loops", False)):
        return {"status": "fail", "message": "logic.rank_strict must refuse combinational loops"}
    if not bool(by_id["logic.lab_experimental"].get("allow_combinational_loops", False)):
        return {"status": "fail", "message": "logic.lab_experimental must declare explicit loop relaxation"}
    if str(by_id["logic.lab_experimental"].get("loop_resolution_mode", "")).strip() != "allow_with_caps":
        return {"status": "fail", "message": "logic.lab_experimental must use allow_with_caps loop resolution"}

    return {"status": "pass", "message": "LOGIC policies declare compute and loop controls"}
