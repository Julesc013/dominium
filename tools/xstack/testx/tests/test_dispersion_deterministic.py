"""FAST test: POLL-1 dispersion tick produces deterministic outputs for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_dispersion_deterministic"
TEST_TAGS = ["fast", "pollution", "determinism", "dispersion"]


def _snapshot(state: dict, pollutant_id: str) -> dict:
    if "src" not in sys.modules:
        pass
    from pollution.dispersion_engine import concentration_field_id_for_pollutant

    field_id = concentration_field_id_for_pollutant(pollutant_id)
    cells = sorted(
        [
            {
                "cell_id": str(row.get("cell_id", row.get("spatial_node_id", ""))).strip(),
                "value": int(row.get("value", 0) or 0),
                "last_updated_tick": int(row.get("last_updated_tick", 0) or 0),
            }
            for row in list(state.get("field_cells") or [])
            if isinstance(row, dict) and str(row.get("field_id", "")).strip() == field_id
        ],
        key=lambda item: str(item.get("cell_id", "")),
    )
    return {
        "cells": cells,
        "pollution_dispersion_step_rows": [dict(row) for row in list(state.get("pollution_dispersion_step_rows") or []) if isinstance(row, dict)],
        "pollution_deposition_rows": [dict(row) for row in list(state.get("pollution_deposition_rows") or []) if isinstance(row, dict)],
        "pollution_dispersion_hash_chain": str(state.get("pollution_dispersion_hash_chain", "")).strip(),
        "pollution_deposition_hash_chain": str(state.get("pollution_deposition_hash_chain", "")).strip(),
        "pollution_field_hash_chain": str(state.get("pollution_field_hash_chain", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_dispersion_testlib import (
        build_pollution_field_inputs,
        execute_pollution_dispersion_tick,
        seed_state_with_pollution_emission,
    )

    pollutant_id = "pollutant.smoke_particulate"
    source_cell_id = "cell.0.0.0"
    state_a = seed_state_with_pollution_emission(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        emitted_mass=96,
        source_cell_id=source_cell_id,
    )
    state_b = copy.deepcopy(state_a)
    inputs = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        cell_ids=["cell.0.0.0", "cell.1.0.0"],
    )

    out_a = execute_pollution_dispersion_tick(repo_root=repo_root, state=state_a, inputs=copy.deepcopy(inputs))
    out_b = execute_pollution_dispersion_tick(repo_root=repo_root, state=state_b, inputs=copy.deepcopy(inputs))
    if str(out_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first dispersion tick failed: {}".format(out_a)}
    if str(out_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second dispersion tick failed: {}".format(out_b)}

    snap_a = _snapshot(state_a, pollutant_id)
    snap_b = _snapshot(state_b, pollutant_id)
    if snap_a != snap_b:
        return {"status": "fail", "message": "dispersion output drifted across equivalent runs"}
    return {"status": "pass", "message": "dispersion tick deterministic snapshot stable"}
