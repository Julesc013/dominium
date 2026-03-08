#!/usr/bin/env python3
"""Verify GEO-6 path queries replay deterministically."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.geo import (  # noqa: E402
    build_path_request,
    geo_path_query,
    path_result_proof_surface,
    traversal_policy_registry_hash,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _cell_key(topology_profile_id: str, chart_id: str, index_tuple: list[int]) -> dict:
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": topology_profile_id,
        "chart_id": chart_id,
        "index_tuple": list(index_tuple),
        "refinement_level": 0,
        "extensions": {},
    }


def _run_once() -> dict:
    fixtures = []
    grid_request = build_path_request(
        request_id="path.fixture.grid",
        start_ref={"geo_cell_key": _cell_key("geo.topology.r2_infinite", "chart.global.r2", [0, 0])},
        goal_ref={"geo_cell_key": _cell_key("geo.topology.r2_infinite", "chart.global.r2", [2, 1])},
        traversal_policy_id="traverse.default_walk",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.r2_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
        },
    )
    fixtures.append(geo_path_query(grid_request))

    torus_request = build_path_request(
        request_id="path.fixture.torus",
        start_ref={"geo_cell_key": _cell_key("geo.topology.torus_r2", "chart.global.r2", [0, 0])},
        goal_ref={"geo_cell_key": _cell_key("geo.topology.torus_r2", "chart.global.r2", [99, 0])},
        traversal_policy_id="traverse.default_walk",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.torus_r2",
            "metric_profile_id": "geo.metric.torus_wrap",
            "partition_profile_id": "geo.partition.grid_zd",
        },
    )
    fixtures.append(geo_path_query(torus_request))

    sphere_request = build_path_request(
        request_id="path.fixture.sphere",
        start_ref={
            "geo_cell_key": {
                "partition_profile_id": "geo.partition.sphere_tiles_stub",
                "topology_profile_id": "geo.topology.sphere_surface_s2",
                "chart_id": "chart.atlas.north",
                "index_tuple": [0, 0],
                "refinement_level": 0,
                "extensions": {},
            }
        },
        goal_ref={
            "geo_cell_key": {
                "partition_profile_id": "geo.partition.sphere_tiles_stub",
                "topology_profile_id": "geo.topology.sphere_surface_s2",
                "chart_id": "chart.atlas.north",
                "index_tuple": [1, 1],
                "refinement_level": 0,
                "extensions": {},
            }
        },
        traversal_policy_id="traverse.default_walk",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.sphere_surface_s2",
            "metric_profile_id": "geo.metric.spherical_geodesic_stub",
            "partition_profile_id": "geo.partition.sphere_tiles_stub",
        },
    )
    fixtures.append(geo_path_query(sphere_request))

    bounded_request = build_path_request(
        request_id="path.fixture.bounded",
        start_ref={"geo_cell_key": _cell_key("geo.topology.r2_infinite", "chart.global.r2", [0, 0])},
        goal_ref={"geo_cell_key": _cell_key("geo.topology.r2_infinite", "chart.global.r2", [20, 0])},
        traversal_policy_id="traverse.portal_allowed_stub",
        tier_mode="meso",
        extensions={
            "topology_profile_id": "geo.topology.r2_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
            "max_expansions": 3,
        },
    )
    fixtures.append(geo_path_query(bounded_request))

    proof_surface = path_result_proof_surface(fixtures)
    observed = []
    for row in fixtures:
        result_row = dict(row.get("path_result") or {})
        observed.append(
            {
                "request_id": str((dict(row.get("path_request") or {})).get("request_id", "")),
                "result": str(row.get("result", "")),
                "result_id": str(result_row.get("result_id", "")),
                "total_cost": int(result_row.get("total_cost", 0) or 0),
                "path_cell_count": len(list(result_row.get("path_cells") or [])),
                "deterministic_fingerprint": str(result_row.get("deterministic_fingerprint", "")),
            }
        )
    return {
        "observed": observed,
        "proof_surface": proof_surface,
        "traversal_policy_registry_hash": traversal_policy_registry_hash(),
        "run_hash": canonical_sha256({"observed": observed, "proof_surface": proof_surface}),
    }


def verify_path_request_replay() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    proof_surface = dict(first.get("proof_surface") or {})
    report = {
        "result": "complete" if stable else "violation",
        "observed": dict(first.get("observed") or {}) if isinstance(first.get("observed"), dict) else list(first.get("observed") or []),
        "proof_surface": proof_surface,
        "traversal_policy_registry_hash": str(first.get("traversal_policy_registry_hash", "")),
        "path_request_hash_chain": str(proof_surface.get("path_request_hash_chain", "")),
        "path_result_hash_chain": str(proof_surface.get("path_result_hash_chain", "")),
        "run_hash": str(first.get("run_hash", "")),
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-6 path replay determinism.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_path_request_replay()
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
