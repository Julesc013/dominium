"""FAST test: POLL-0 emitted mass equals authoritative total mass accumulation."""

from __future__ import annotations

import sys


TEST_ID = "test_pollution_totals_conserved"
TEST_TAGS = ["fast", "pollution", "conservation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_testlib import execute_pollution_emit, seed_pollution_state

    state = seed_pollution_state()
    inputs = {
        "policy_id": "poll.policy.rank_strict",
        "events": [
            {
                "origin_kind": "fire",
                "origin_id": "event.fire.001",
                "pollutant_id": "pollutant.smoke_particulate",
                "emitted_mass": 6,
                "spatial_scope_id": "region.alpha",
            },
            {
                "origin_kind": "fire",
                "origin_id": "event.fire.002",
                "pollutant_id": "pollutant.smoke_particulate",
                "emitted_mass": 5,
                "spatial_scope_id": "region.alpha",
            },
            {
                "origin_kind": "reaction",
                "origin_id": "run.chem.001",
                "pollutant_id": "pollutant.co2_stub",
                "emitted_mass": 4,
                "spatial_scope_id": "region.alpha",
            },
        ],
    }
    expected_emitted_mass = 6 + 5 + 4

    out = execute_pollution_emit(repo_root=repo_root, state=state, inputs=inputs)
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "pollution emit failed: {}".format(out)}

    source_rows = [dict(row) for row in list(state.get("pollution_source_event_rows") or []) if isinstance(row, dict)]
    total_rows = [dict(row) for row in list(state.get("pollution_total_rows") or []) if isinstance(row, dict)]
    if not source_rows:
        return {"status": "fail", "message": "missing pollution_source_event_rows"}
    if not total_rows:
        return {"status": "fail", "message": "missing pollution_total_rows"}

    source_mass = sum(int(max(0, int(row.get("emitted_mass", 0) or 0))) for row in source_rows)
    total_mass = sum(int(max(0, int(row.get("pollutant_mass_total", 0) or 0))) for row in total_rows)
    if source_mass != expected_emitted_mass:
        return {"status": "fail", "message": "source mass mismatch: expected {} got {}".format(expected_emitted_mass, source_mass)}
    if total_mass != expected_emitted_mass:
        return {"status": "fail", "message": "total mass mismatch: expected {} got {}".format(expected_emitted_mass, total_mass)}
    return {"status": "pass", "message": "pollution totals conserved for emitted mass"}
