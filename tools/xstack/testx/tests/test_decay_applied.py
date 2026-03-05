"""FAST test: POLL-1 decay model applies deterministic decay mass during dispersion."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_decay_applied"
TEST_TAGS = ["fast", "pollution", "dispersion", "decay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_dispersion_testlib import (
        build_pollution_field_inputs,
        execute_pollution_dispersion_tick,
        seed_state_with_pollution_emission,
    )

    state = seed_state_with_pollution_emission(
        repo_root=repo_root,
        pollutant_id="pollutant.smoke_particulate",
        emitted_mass=160,
        source_cell_id="cell.0.0.0",
    )
    inputs = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id="pollutant.smoke_particulate",
        cell_ids=["cell.0.0.0"],
    )
    out = execute_pollution_dispersion_tick(repo_root=repo_root, state=state, inputs=copy.deepcopy(inputs))
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "dispersion tick failed: {}".format(out)}

    step_rows = [
        dict(row)
        for row in list(state.get("pollution_dispersion_step_rows") or [])
        if isinstance(row, dict)
        and str(row.get("pollutant_id", "")).strip() == "pollutant.smoke_particulate"
    ]
    if not step_rows:
        return {"status": "fail", "message": "no dispersion step rows found for smoke pollutant"}
    if not any(int(row.get("decay_mass", 0) or 0) > 0 for row in step_rows):
        return {"status": "fail", "message": "expected positive decay_mass for half-life decay model"}
    return {"status": "pass", "message": "decay mass applied for smoke half-life model"}
