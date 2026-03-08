#!/usr/bin/env python3
"""Replay GEO-10 stress windows and verify GEO proof surfaces remain stable."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.geo.geo10_stress_runtime import (  # noqa: E402
    _as_int,
    _as_map,
    _cell_key_hash,
    _hash_chain,
    _suite_geometry_and_compaction,
    _suite_metrics_and_pathing,
    _suite_projection_and_views,
    _suite_report,
    _suite_worldgen_and_overlay,
    load_geo_stress_scenario,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _truth_hash_anchor(scenario: Mapping[str, object]) -> str:
    suites = [dict(row) for row in list(scenario.get("topology_suites") or []) if isinstance(row, Mapping)]
    return canonical_sha256(
        {
            "scenario_id": str(scenario.get("scenario_id", "")).strip(),
            "scenario_seed": int(max(0, _as_int(scenario.get("scenario_seed", 0), 0))),
            "suite_fingerprints": [str(row.get("deterministic_fingerprint", "")).strip() for row in suites],
        }
    )


def _selected_suites(scenario: Mapping[str, object], suite_id: str) -> list[dict]:
    rows = [dict(row) for row in list(scenario.get("topology_suites") or []) if isinstance(row, Mapping)]
    token = str(suite_id or "").strip()
    if not token:
        return sorted(rows, key=lambda row: str(row.get("suite_id", "")))
    return [dict(row) for row in rows if str(row.get("suite_id", "")).strip() == token]


def _cell_key_chain_for_window(*, suite: Mapping[str, object], view_data: Mapping[str, object], path_result: Mapping[str, object]) -> str:
    projection_rows = [dict(row) for row in list(_as_map(view_data.get("projection_result")).get("projected_cells") or []) if isinstance(row, Mapping)]
    path_cells = [dict(row) for row in list(_as_map(path_result.get("path_result")).get("path_cells") or []) if isinstance(row, Mapping)]
    cell_rows = [
        {"geo_cell_key": dict(_as_map(suite.get("center_cell_key")))},
        {"geo_cell_key": dict(_as_map(suite.get("goal_cell_key")))},
    ]
    cell_rows.extend(projection_rows)
    cell_rows.extend({"geo_cell_key": dict(row)} for row in path_cells)
    return _hash_chain(
        cell_rows,
        key_fn=lambda row: str(_cell_key_hash(_as_map(_as_map(row).get("geo_cell_key")))),
    )


def _suite_window_snapshot(*, suite: Mapping[str, object], scenario: Mapping[str, object], truth_hash_anchor: str) -> dict:
    suite_report = _suite_report(suite=suite, scenario=scenario, truth_hash_anchor=truth_hash_anchor)
    degradation_report = _as_map(suite_report.get("degradation_report"))
    suite_metrics = _suite_metrics_and_pathing(
        suite=suite,
        scenario=scenario,
        noncritical_neighbor_radius=int(_as_int(degradation_report.get("effective_neighbor_radius_noncritical", 1), 1)),
        path_max_expansions=int(_as_int(degradation_report.get("effective_path_max_expansions", 48), 48)),
    )
    geometry_data = _suite_geometry_and_compaction(suite=suite, scenario=scenario)
    view_data = _suite_projection_and_views(
        suite=suite,
        geometry_rows=geometry_data.get("geometry_rows"),
        scenario_truth_anchor=truth_hash_anchor,
        resolution_spec_override=_as_map(degradation_report.get("effective_resolution_spec")),
        defer_derived_views=bool(degradation_report.get("defer_derived_views", False)),
    )
    world_overlay = _suite_worldgen_and_overlay(suite=suite, scenario=scenario)
    snapshot = {
        "suite_id": str(suite.get("suite_id", "")).strip(),
        "suite_report_fingerprint": str(suite_report.get("deterministic_fingerprint", "")).strip(),
        "cell_key_hash_chain": _cell_key_chain_for_window(
            suite=suite,
            view_data=view_data,
            path_result=_as_map(suite_metrics.get("path_result")),
        ),
        "distance_query_fingerprint": str(_as_map(_as_map(suite_metrics.get("distance_probe")).get("first")).get("deterministic_fingerprint", "")).strip(),
        "metric_query_hash_chain": str(_as_map(suite_report.get("proof_summary")).get("metric_query_hash_chain", "")).strip(),
        "field_sample_hash": canonical_sha256(
            {
                "position_sample": _as_map(suite_metrics.get("field_position_sample")),
                "neighborhood_sample": _as_map(suite_metrics.get("field_neighborhood_sample")),
            }
        ),
        "overlay_manifest_hash": str(_as_map(world_overlay.get("overlay_surface")).get("overlay_manifest_hash", "")).strip(),
        "overlay_merge_result_hash_chain": str(
            _as_map(world_overlay.get("overlay_surface")).get("overlay_merge_result_hash_chain", "")
        ).strip(),
        "geometry_state_hash_chain": str(_as_map(geometry_data.get("geometry_surface")).get("deterministic_fingerprint", "")).strip(),
        "geometry_edit_event_hash_chain": str(
            _as_map(geometry_data.get("geometry_surface")).get("geometry_edit_event_hash_chain", "")
        ).strip(),
        "worldgen_result_hash_chain": str(_as_map(world_overlay.get("worldgen_surface")).get("worldgen_result_hash_chain", "")).strip(),
        "projection_view_fingerprint": str(view_data.get("view_fingerprint", "")).strip(),
        "path_result_hash_chain": str(_as_map(suite_report.get("proof_summary")).get("path_result_hash_chain", "")).strip(),
        "degradation_hash_chain": str(_as_map(suite_report.get("proof_summary")).get("geo_degradation_hash_chain", "")).strip(),
        "suite_assertions": dict(_as_map(suite_report.get("assertions"))),
    }
    snapshot["deterministic_fingerprint"] = canonical_sha256(dict(snapshot, deterministic_fingerprint=""))
    return snapshot


def _run_once(*, scenario: Mapping[str, object], suite_id: str) -> dict:
    truth_hash_anchor = _truth_hash_anchor(scenario)
    suite_rows = _selected_suites(scenario, suite_id)
    suite_snapshots = [
        _suite_window_snapshot(suite=row, scenario=scenario, truth_hash_anchor=truth_hash_anchor)
        for row in suite_rows
    ]
    return {
        "scenario_id": str(scenario.get("scenario_id", "")).strip(),
        "truth_hash_anchor": truth_hash_anchor,
        "suite_snapshots": suite_snapshots,
        "run_hash": canonical_sha256(
            {
                "scenario_id": str(scenario.get("scenario_id", "")).strip(),
                "truth_hash_anchor": truth_hash_anchor,
                "suite_snapshots": suite_snapshots,
            }
        ),
    }


def replay_geo_window(*, scenario: Mapping[str, object], suite_id: str = "") -> dict:
    first = _run_once(scenario=scenario, suite_id=suite_id)
    second = _run_once(scenario=scenario, suite_id=suite_id)
    stable = first == second
    suite_rows = [dict(row) for row in list(first.get("suite_snapshots") or []) if isinstance(row, Mapping)]
    suite_results = {
        str(row.get("suite_id", "")).strip(): {
            "stable": stable,
            "assertions": dict(_as_map(row.get("suite_assertions"))),
        }
        for row in suite_rows
    }
    report = {
        "result": "complete"
        if stable and all(all(bool(value) for value in dict(item.get("assertions") or {}).values()) for item in suite_results.values())
        else "violation",
        "scenario_id": str(first.get("scenario_id", "")),
        "truth_hash_anchor": str(first.get("truth_hash_anchor", "")),
        "suite_results": suite_results,
        "observed": first,
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay GEO-10 stress windows and verify proof surfaces.")
    parser.add_argument("--scenario", default="build/geo/geo10_stress_scenario.json")
    parser.add_argument("--suite-id", default="")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    scenario = load_geo_stress_scenario(str(args.scenario or "").strip())
    report = replay_geo_window(scenario=scenario, suite_id=str(args.suite_id or "").strip())
    output_path = str(args.output_path or "").strip()
    if output_path:
        abs_path = os.path.normpath(os.path.abspath(output_path))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
