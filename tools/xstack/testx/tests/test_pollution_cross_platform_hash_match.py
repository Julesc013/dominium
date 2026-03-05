"""FAST test: POLL-1 hash chains are stable across input ordering permutations."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_pollution_cross_platform_hash_match"
TEST_TAGS = ["fast", "pollution", "hash", "determinism"]


def _hash_tuple(state: dict) -> tuple[str, str, str, str]:
    return (
        str(state.get("pollution_dispersion_hash_chain", "")).strip(),
        str(state.get("pollution_deposition_hash_chain", "")).strip(),
        str(state.get("pollution_field_hash_chain", "")).strip(),
        str(state.get("pollution_exposure_hash_chain", "")).strip(),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_dispersion_testlib import (
        build_pollution_field_inputs,
        execute_pollution_dispersion_tick,
        seed_state_with_pollution_emission,
    )

    pollutant_id = "pollutant.oil_spill_stub"
    state_a = seed_state_with_pollution_emission(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        emitted_mass=90,
        source_cell_id="cell.1.0.0",
        origin_kind="leak",
    )
    state_b = copy.deepcopy(state_a)
    state_b["pollution_source_event_rows"] = list(
        reversed([dict(row) for row in list(state_b.get("pollution_source_event_rows") or []) if isinstance(row, dict)])
    )

    inputs_a = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        cell_ids=["cell.0.0.0", "cell.1.0.0", "cell.2.0.0"],
        reverse_order=False,
    )
    inputs_b = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        cell_ids=["cell.0.0.0", "cell.1.0.0", "cell.2.0.0"],
        reverse_order=True,
    )

    out_a = execute_pollution_dispersion_tick(repo_root=repo_root, state=state_a, inputs=copy.deepcopy(inputs_a))
    out_b = execute_pollution_dispersion_tick(repo_root=repo_root, state=state_b, inputs=copy.deepcopy(inputs_b))
    if str(out_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ordering baseline run failed: {}".format(out_a)}
    if str(out_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ordering permuted run failed: {}".format(out_b)}

    if _hash_tuple(state_a) != _hash_tuple(state_b):
        return {"status": "fail", "message": "pollution hash chains diverged under ordering permutation"}
    return {"status": "pass", "message": "pollution hash chains remain stable across ordering permutation"}
