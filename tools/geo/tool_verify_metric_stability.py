#!/usr/bin/env python3
"""Verify GEO-3 metric query stability for deterministic fixtures."""

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
    geo_distance,
    geo_geodesic,
    geo_neighbors,
    metric_query_proof_surface,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _run_once() -> dict:
    euclidean = geo_distance(
        {"x": 0, "y": 0, "z": 0},
        {"x": 3000, "y": 4000, "z": 0},
        "geo.topology.r3_infinite",
        "geo.metric.euclidean",
    )
    torus = geo_distance(
        {"coords": [0, 0]},
        {"coords": [990000, 0]},
        "geo.topology.torus_r2",
        "geo.metric.torus_wrap",
    )
    spherical = geo_geodesic(
        {"coords": [0, 0]},
        {"coords": [0, 1000]},
        "geo.topology.sphere_surface_s2",
        "geo.metric.spherical_geodesic_stub",
    )
    grid_neighbors = geo_neighbors(
        "cell.0.0",
        "geo.topology.r2_infinite",
        1,
        "geo.metric.euclidean",
    )
    torus_neighbors = geo_neighbors(
        "cell.0.0",
        "geo.topology.torus_r2",
        1,
        "geo.metric.torus_wrap",
        "geo.partition.grid_zd",
    )
    observed = {
        "distance_queries": [
            {
                "fixture_id": "fixture.metric.euclidean_exact",
                "topology_profile_id": str(euclidean.get("topology_profile_id", "")),
                "metric_profile_id": str(euclidean.get("metric_profile_id", "")),
                "distance_mm": int(euclidean.get("distance_mm", 0) or 0),
                "error_bound_mm": int(euclidean.get("error_bound_mm", 0) or 0),
                "deterministic_fingerprint": str(euclidean.get("deterministic_fingerprint", "")),
            },
            {
                "fixture_id": "fixture.metric.torus_wrap_exact",
                "topology_profile_id": str(torus.get("topology_profile_id", "")),
                "metric_profile_id": str(torus.get("metric_profile_id", "")),
                "distance_mm": int(torus.get("distance_mm", 0) or 0),
                "error_bound_mm": int(torus.get("error_bound_mm", 0) or 0),
                "deterministic_fingerprint": str(torus.get("deterministic_fingerprint", "")),
            },
        ],
        "geodesic_queries": [
            {
                "fixture_id": "fixture.metric.spherical_geodesic_stub",
                "topology_profile_id": str(spherical.get("topology_profile_id", "")),
                "metric_profile_id": str(spherical.get("metric_profile_id", "")),
                "geodesic_mm": int(spherical.get("geodesic_mm", 0) or 0),
                "error_bound_mm": int(spherical.get("error_bound_mm", 0) or 0),
                "deterministic_fingerprint": str(spherical.get("deterministic_fingerprint", "")),
            }
        ],
        "neighbor_queries": [
            {
                "fixture_id": "fixture.metric.grid_neighbors",
                "topology_profile_id": str(grid_neighbors.get("topology_profile_id", "")),
                "metric_profile_id": str(grid_neighbors.get("metric_profile_id", "")),
                "neighbors": list(grid_neighbors.get("neighbors") or []),
                "deterministic_fingerprint": str(grid_neighbors.get("deterministic_fingerprint", "")),
            },
            {
                "fixture_id": "fixture.metric.torus_neighbors",
                "topology_profile_id": str(torus_neighbors.get("topology_profile_id", "")),
                "metric_profile_id": str(torus_neighbors.get("metric_profile_id", "")),
                "neighbors": list(torus_neighbors.get("neighbors") or []),
                "deterministic_fingerprint": str(torus_neighbors.get("deterministic_fingerprint", "")),
            },
        ],
    }
    proof_surface = metric_query_proof_surface([euclidean, torus, spherical, grid_neighbors, torus_neighbors])
    return {
        "observed": observed,
        "proof_surface": proof_surface,
        "run_hash": canonical_sha256({"observed": observed, "proof_surface": proof_surface}),
    }


def verify_metric_stability() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    report = {
        "result": "complete" if stable else "violation",
        "proof_surface": dict(first.get("proof_surface") or {}),
        "observed": dict(first.get("observed") or {}),
        "run_hash": str(first.get("run_hash", "")),
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-3 metric query replay stability.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_metric_stability()
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
