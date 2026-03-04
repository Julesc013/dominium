"""FAST test: CHEM-3 maintenance actions reduce degradation levels and emit reset records."""

from __future__ import annotations

import sys


TEST_ID = "test_maintenance_resets_levels_logged"
TEST_TAGS = ["fast", "chem", "maintenance", "degradation", "logging"]


def _corrosion_level(state: dict, target_id: str) -> int:
    for row in list(state.get("chem_degradation_state_rows") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("target_id", "")).strip() != target_id:
            continue
        if str(row.get("degradation_kind_id", "")).strip() != "corrosion":
            continue
        return int(max(0, int(row.get("level_value", 0) or 0)))
    return 0


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem_degradation_testlib import execute_process, seed_degradation_state

    target_id = "asset.chem.pipe.maint"
    state = seed_degradation_state()
    degrade = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.degradation_tick",
        inputs={
            "target_id": target_id,
            "profile_id": "profile.pipe_steel_basic",
            "target_kind": "asset",
            "parameters": {
                "temperature": 37915,
                "moisture": 550,
                "radiation_intensity": 280,
                "entropy_value": 420,
                "fluid_composition_tags": ["tag.fluid.corrosive"],
            },
        },
    )
    if str(degrade.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "pre-maintenance degradation_tick refused"}

    before_level = _corrosion_level(state, target_id)
    if before_level <= 0:
        return {"status": "fail", "message": "fixture should produce non-zero corrosion before maintenance"}

    maintenance = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.apply_coating",
        inputs={
            "target_id": target_id,
            "reset_permille": 600,
            "reason_code": "test.maintenance.apply_coating",
        },
    )
    if str(maintenance.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process.apply_coating refused in maintenance reset fixture"}
    if int(max(0, int(maintenance.get("reset_count", 0) or 0))) <= 0:
        return {"status": "fail", "message": "maintenance response did not report any reset rows"}

    after_level = _corrosion_level(state, target_id)
    if after_level >= before_level:
        return {
            "status": "fail",
            "message": "maintenance should reduce corrosion level (before={}, after={})".format(
                before_level,
                after_level,
            ),
        }

    reset_events = [
        dict(row)
        for row in list(state.get("chem_degradation_event_rows") or [])
        if isinstance(row, dict)
        and str(row.get("target_id", "")).strip() == target_id
        and str(row.get("degradation_kind_id", "")).strip() == "corrosion"
        and str(row.get("event_id", "")).strip().startswith("event.chem.degradation.reset.")
        and str((dict(row.get("extensions") or {})).get("source_process_id", "")).strip() == "process.apply_coating"
    ]
    if not reset_events:
        return {"status": "fail", "message": "missing normalized degradation reset event for maintenance action"}

    artifact_type_ids = sorted(
        set(
            str((dict(row.get("extensions") or {})).get("artifact_type_id", "")).strip()
            for row in list(state.get("info_artifact_rows") or [])
            if isinstance(row, dict)
        )
    )
    if "artifact.record.chem_degradation_reset" not in set(artifact_type_ids):
        return {"status": "fail", "message": "maintenance reset artifact was not emitted"}
    return {"status": "pass", "message": "maintenance resets degradation levels with deterministic logging"}
