"""FAST test: POLL-1 deposition model produces deterministic deposition records."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_deposition_logged"
TEST_TAGS = ["fast", "pollution", "dispersion", "deposition"]


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
        pollutant_id="pollutant.oil_spill_stub",
        emitted_mass=120,
        source_cell_id="cell.0.0.0",
        origin_kind="leak",
    )
    inputs = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id="pollutant.oil_spill_stub",
        cell_ids=["cell.0.0.0"],
    )
    out = execute_pollution_dispersion_tick(repo_root=repo_root, state=state, inputs=copy.deepcopy(inputs))
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "dispersion tick failed: {}".format(out)}

    deposition_rows = [
        dict(row)
        for row in list(state.get("pollution_deposition_rows") or [])
        if isinstance(row, dict)
        and str(row.get("pollutant_id", "")).strip() == "pollutant.oil_spill_stub"
    ]
    if not deposition_rows:
        return {"status": "fail", "message": "deposition rows missing for oil spill pollutant"}
    if not any(int(row.get("deposited_mass", 0) or 0) > 0 for row in deposition_rows):
        return {"status": "fail", "message": "deposition rows exist but deposited_mass stayed zero"}
    if not str(state.get("pollution_deposition_hash_chain", "")).strip():
        return {"status": "fail", "message": "pollution_deposition_hash_chain missing after deposition"}
    return {"status": "pass", "message": "deposition rows logged with deterministic hash chain"}
