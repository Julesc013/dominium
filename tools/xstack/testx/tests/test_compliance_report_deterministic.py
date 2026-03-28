"""FAST test: POLL-2 compliance report generation is deterministic across equivalent runs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_compliance_report_deterministic"
TEST_TAGS = ["fast", "pollution", "compliance", "determinism"]


def _snapshot(state: dict) -> dict:
    return {
        "pollution_compliance_report_rows": [
            dict(row)
            for row in list(state.get("pollution_compliance_report_rows") or [])
            if isinstance(row, dict)
        ],
        "pollution_compliance_violation_rows": [
            dict(row)
            for row in list(state.get("pollution_compliance_violation_rows") or [])
            if isinstance(row, dict)
        ],
        "pollution_compliance_report_hash_chain": str(
            state.get("pollution_compliance_report_hash_chain", "")
        ).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell
    from pollution.dispersion_engine import concentration_field_id_for_pollutant
    from tools.xstack.testx.tests.pollution_testlib import (
        execute_pollution_compliance_tick,
        seed_pollution_state,
    )

    pollutant_id = "pollutant.smoke_particulate"
    field_id = concentration_field_id_for_pollutant(pollutant_id)
    state_a = seed_pollution_state()
    state_a["field_cells"] = [
        build_field_cell(
            field_id=field_id,
            cell_id="cell.r0",
            value=18,
            last_updated_tick=0,
            value_kind="scalar",
        ),
        build_field_cell(
            field_id=field_id,
            cell_id="cell.r1",
            value=34,
            last_updated_tick=0,
            value_kind="scalar",
        ),
    ]
    state_b = copy.deepcopy(state_a)
    inputs = {
        "observed_statistic": "avg",
        "region_cell_map": {"region.pollution.a": ["cell.r0", "cell.r1"]},
        "channel_id": "channel.pollution.missing",
    }
    policy_overrides = {
        "exposure_threshold_registry": {
            "record": {
                "exposure_thresholds": [
                    {
                        "pollutant_id": pollutant_id,
                        "warning_threshold": 10,
                        "critical_threshold": 20,
                    }
                ]
            }
        }
    }

    out_a = execute_pollution_compliance_tick(
        repo_root=repo_root,
        state=state_a,
        inputs=copy.deepcopy(inputs),
        policy_overrides=copy.deepcopy(policy_overrides),
    )
    out_b = execute_pollution_compliance_tick(
        repo_root=repo_root,
        state=state_b,
        inputs=copy.deepcopy(inputs),
        policy_overrides=copy.deepcopy(policy_overrides),
    )
    if str(out_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first compliance run failed: {}".format(out_a)}
    if str(out_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second compliance run failed: {}".format(out_b)}

    snap_a = _snapshot(state_a)
    snap_b = _snapshot(state_b)
    if snap_a != snap_b:
        return {"status": "fail", "message": "compliance report output drifted across equivalent runs"}
    if not snap_a["pollution_compliance_report_rows"]:
        return {"status": "fail", "message": "compliance report rows were not produced"}
    return {"status": "pass", "message": "compliance report generation remains deterministic"}
