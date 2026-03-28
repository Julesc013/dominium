"""Deterministic GAL-0 galaxy-proxy probes for replay and TestX reuse."""

from __future__ import annotations

import os
import sys
from typing import Dict, Iterable, List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from geo import generate_worldgen_result  # noqa: E402
from worldgen.galaxy import build_galaxy_proxy_update_plan, galaxy_proxy_window_hash  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import execute_intent  # noqa: E402
from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row  # noqa: E402
from tools.xstack.testx.tests.mobility_free_testlib import authority_context, law_profile, policy_context  # noqa: E402


GAL0_ALLOWED_PROCESSES = ["process.field_update"]
GAL0_REPLAY_TICK = 2048
GAL0_SAMPLE_CELL_INDICES = (
    [0, 0, 0],
    [800, 0, 0],
    [4200, 0, 0],
    [5200, 0, 2200],
)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _field_projection_hash(state: Mapping[str, object]) -> str:
    rows = []
    for raw in _as_list(_as_map(state).get("field_cells")):
        row = _as_map(raw)
        field_id = str(row.get("field_id", "")).strip()
        if field_id not in {
            "field.stellar_density_proxy.galaxy",
            "field.metallicity_proxy.galaxy",
            "field.radiation_background_proxy.galaxy",
            "field.galactic_region_id.galaxy",
        }:
            continue
        rows.append(
            {
                "field_id": field_id,
                "cell_id": str(row.get("cell_id", "")).strip(),
                "value": row.get("value"),
                "geo_cell_key": _as_map(_as_map(row.get("extensions")).get("geo_cell_key")),
            }
        )
    rows.sort(key=lambda item: (item["field_id"], item["cell_id"]))
    return canonical_sha256(rows)


def _seed_galaxy_proxy_state(
    worldgen_results: Sequence[Mapping[str, object]],
    *,
    universe_identity: Mapping[str, object],
    simulation_tick: int,
) -> dict:
    state = seed_worldgen_state()
    state["simulation_time"] = {"tick": int(max(0, int(simulation_tick)))}
    state["universe_identity"] = dict(universe_identity)
    layer_by_id: Dict[str, dict] = {}
    field_cells: List[dict] = []
    for raw in list(worldgen_results or []):
        row = _as_map(raw)
        for field_row in _as_list(row.get("field_layers")):
            if not isinstance(field_row, Mapping):
                continue
            field_id = str(field_row.get("field_id", "")).strip()
            if field_id:
                layer_by_id[field_id] = dict(field_row)
        for field_row in _as_list(row.get("field_initializations")):
            if isinstance(field_row, Mapping):
                field_cells.append(dict(field_row))
    state["field_layers"] = [dict(layer_by_id[key]) for key in sorted(layer_by_id.keys())]
    state["field_cells"] = list(field_cells)
    state["worldgen_results"] = [dict(row) for row in list(worldgen_results or []) if isinstance(row, Mapping)]
    return state


def generate_galaxy_proxy_fixture(
    repo_root: str,
    *,
    current_tick: int = 0,
    cell_indices: Iterable[Sequence[int]] = GAL0_SAMPLE_CELL_INDICES,
) -> dict:
    state = seed_worldgen_state()
    universe_identity = _as_map(state.get("universe_identity"))
    results: List[dict] = []
    for index_tuple in list(cell_indices):
        result = generate_worldgen_result(
            universe_identity=universe_identity,
            worldgen_request=worldgen_request_row(
                request_id="gal0.fixture.{}".format(".".join(str(int(item)) for item in list(index_tuple or []))),
                index_tuple=[int(item) for item in list(index_tuple or [])],
                refinement_level=1,
                reason="query",
            ),
            current_tick=int(current_tick),
            cache_enabled=False,
        )
        if str(result.get("result", "")).strip() != "complete":
            raise RuntimeError("GAL-0 fixture worldgen did not complete for {}".format(list(index_tuple or [])))
        results.append(dict(result))
    return {
        "universe_identity": universe_identity,
        "worldgen_results": results,
        "deterministic_fingerprint": canonical_sha256(
            {
                "current_tick": int(current_tick),
                "cell_indices": [[int(item) for item in list(index_tuple or [])] for index_tuple in list(cell_indices or [])],
            }
        ),
    }


def run_galaxy_proxy_replay(
    repo_root: str,
    *,
    current_tick: int = GAL0_REPLAY_TICK,
    cell_indices: Iterable[Sequence[int]] = GAL0_SAMPLE_CELL_INDICES,
) -> dict:
    fixture = generate_galaxy_proxy_fixture(repo_root, current_tick=current_tick, cell_indices=cell_indices)
    worldgen_results = [dict(row) for row in _as_list(fixture.get("worldgen_results")) if isinstance(row, Mapping)]
    state = _seed_galaxy_proxy_state(
        worldgen_results,
        universe_identity=_as_map(fixture.get("universe_identity")),
        simulation_tick=int(current_tick),
    )
    update_plan = build_galaxy_proxy_update_plan(worldgen_results=worldgen_results, current_tick=int(current_tick))
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.gal0.field_update.{}".format(int(current_tick)),
            "process_id": "process.field_update",
            "inputs": {
                "field_updates": [dict(row) for row in list(update_plan.get("field_updates") or []) if isinstance(row, Mapping)],
            },
        },
        law_profile=law_profile(GAL0_ALLOWED_PROCESSES),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=policy_context(max_compute_units_per_tick=4096),
    )
    evaluations = [dict(row) for row in list(update_plan.get("evaluations") or []) if isinstance(row, Mapping)]
    report = {
        "result": "complete" if str(result.get("result", "")).strip() == "complete" else "refused",
        "current_tick": int(current_tick),
        "worldgen_result_count": int(len(worldgen_results)),
        "evaluation_count": int(len(evaluations)),
        "applied_update_count": int(result.get("applied_update_count", 0) or 0),
        "proxy_window_hash": galaxy_proxy_window_hash(evaluations),
        "field_projection_hash": _field_projection_hash(state),
        "update_plan_fingerprint": str(update_plan.get("deterministic_fingerprint", "")).strip(),
        "process_result_fingerprint": str(result.get("deterministic_fingerprint", "")).strip(),
        "field_update_hash_chain": str(state.get("field_update_hash_chain", "")).strip(),
        "evaluations": evaluations,
        "cell_regions": dict(
            (
                str(row.get("cell_id", "")).strip(),
                str(row.get("galactic_region_id", "")).strip(),
            )
            for row in evaluations
            if str(row.get("cell_id", "")).strip()
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_galaxy_proxy_window_replay(repo_root: str) -> dict:
    first = run_galaxy_proxy_replay(repo_root)
    second = run_galaxy_proxy_replay(repo_root)
    stable = (
        first.get("result") == "complete"
        and second.get("result") == "complete"
        and str(first.get("proxy_window_hash", "")).strip() == str(second.get("proxy_window_hash", "")).strip()
        and str(first.get("field_projection_hash", "")).strip() == str(second.get("field_projection_hash", "")).strip()
        and str(first.get("field_update_hash_chain", "")).strip() == str(second.get("field_update_hash_chain", "")).strip()
    )
    payload = {
        "result": "complete" if stable else "drift",
        "stable_across_repeated_runs": bool(stable),
        "first_run": dict(first),
        "second_run": dict(second),
        "combined_hash": canonical_sha256(
            {
                "first_proxy_window_hash": str(first.get("proxy_window_hash", "")).strip(),
                "first_field_projection_hash": str(first.get("field_projection_hash", "")).strip(),
                "second_proxy_window_hash": str(second.get("proxy_window_hash", "")).strip(),
                "second_field_projection_hash": str(second.get("field_projection_hash", "")).strip(),
            }
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def region_threshold_report(repo_root: str) -> dict:
    report = run_galaxy_proxy_replay(repo_root)
    expected = {
        "cell.0.0.0": "region.bulge",
        "cell.800.0.0": "region.inner_disk",
        "cell.4200.0.0": "region.outer_disk",
        "cell.5200.0.2200": "region.halo",
    }
    actual = dict(report.get("cell_regions") or {})
    mismatches = []
    for cell_id, expected_region in sorted(expected.items()):
        observed = str(actual.get(cell_id, "")).strip()
        if observed != expected_region:
            mismatches.append(
                {
                    "cell_id": cell_id,
                    "expected_region": expected_region,
                    "observed_region": observed,
                }
            )
    payload = {
        "result": "complete" if not mismatches else "mismatch",
        "mismatch_count": int(len(mismatches)),
        "mismatches": mismatches,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def galaxy_proxy_hash(repo_root: str) -> str:
    return str(verify_galaxy_proxy_window_replay(repo_root).get("combined_hash", "")).strip()


__all__ = [
    "GAL0_REPLAY_TICK",
    "GAL0_SAMPLE_CELL_INDICES",
    "galaxy_proxy_hash",
    "generate_galaxy_proxy_fixture",
    "region_threshold_report",
    "run_galaxy_proxy_replay",
    "verify_galaxy_proxy_window_replay",
]
