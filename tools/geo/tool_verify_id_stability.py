#!/usr/bin/env python3
"""Verify GEO-1 cell-key and object-ID stability for deterministic fixtures."""

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

from geo import (  # noqa: E402
    geo_cell_key_from_position,
    geo_object_id,
    geo_refine_cell_key,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


_FIXTURES = (
    {
        "fixture_id": "fixture.geo.grid_r3.star_system",
        "position": {"x": 12345, "y": -23456, "z": 999999},
        "topology_profile_id": "geo.topology.r3_infinite",
        "partition_profile_id": "geo.partition.grid_zd",
        "chart_id": "chart.global.r3",
        "object_kind_id": "kind.star_system",
        "local_subkey": "system:0",
        "refine_to": 1,
    },
    {
        "fixture_id": "fixture.geo.torus_r2.surface_tile",
        "position": {"x": 1010000, "y": -10000},
        "topology_profile_id": "geo.topology.torus_r2",
        "partition_profile_id": "geo.partition.grid_zd",
        "chart_id": "chart.global.r2",
        "object_kind_id": "kind.surface_tile",
        "local_subkey": "tile:0",
        "refine_to": 2,
    },
    {
        "fixture_id": "fixture.geo.sphere_surface.tile",
        "position": {"coords": [45000, 90000]},
        "topology_profile_id": "geo.topology.sphere_surface_s2",
        "partition_profile_id": "geo.partition.sphere_tiles_stub",
        "chart_id": "",
        "object_kind_id": "kind.surface_tile",
        "local_subkey": "tile:12",
        "refine_to": 1,
    },
    {
        "fixture_id": "fixture.geo.r4.signal_node",
        "position": {"coords": [1000, 2000, 3000, 4000]},
        "topology_profile_id": "geo.topology.r4_stub",
        "partition_profile_id": "geo.partition.grid_zd",
        "chart_id": "chart.global.r4",
        "object_kind_id": "kind.signal_node",
        "local_subkey": "signal:0",
        "refine_to": 0,
    },
)


def _fixture_report(universe_identity_hash: str, fixture: Mapping[str, object]) -> dict:
    cell_payload = geo_cell_key_from_position(
        _as_map(fixture.get("position")),
        str(fixture.get("topology_profile_id", "")),
        str(fixture.get("partition_profile_id", "")),
        str(fixture.get("chart_id", "")),
    )
    cell_key = _as_map(cell_payload.get("cell_key"))
    refined_payload = geo_refine_cell_key(
        cell_key,
        int(fixture.get("refine_to", 0) or 0),
    )
    refined_cell_key = _as_map(refined_payload.get("child_cell_key")) or cell_key
    object_payload = geo_object_id(
        str(universe_identity_hash),
        refined_cell_key,
        str(fixture.get("object_kind_id", "")),
        fixture.get("local_subkey"),
    )
    return {
        "fixture_id": str(fixture.get("fixture_id", "")),
        "topology_profile_id": str(fixture.get("topology_profile_id", "")),
        "partition_profile_id": str(fixture.get("partition_profile_id", "")),
        "chart_id": str(_as_map(refined_cell_key).get("chart_id", "")),
        "cell_key_hash": canonical_sha256(_as_map(refined_cell_key)),
        "cell_key_fingerprint": str(_as_map(refined_cell_key).get("deterministic_fingerprint", "")),
        "object_kind_id": str(fixture.get("object_kind_id", "")),
        "local_subkey": fixture.get("local_subkey"),
        "object_id_hash": str(object_payload.get("object_id_hash", "")),
    }


def verify_id_stability(*, universe_identity_hash: str = "universe.identity.fixture") -> dict:
    run_a = [_fixture_report(universe_identity_hash, fixture) for fixture in _FIXTURES]
    run_b = [_fixture_report(universe_identity_hash, fixture) for fixture in _FIXTURES]
    stable = run_a == run_b
    report = {
        "result": "complete" if stable else "violation",
        "universe_identity_hash": str(universe_identity_hash),
        "fixtures": run_a,
        "run_hash": canonical_sha256(run_a),
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-1 deterministic cell-key and object-ID stability.")
    parser.add_argument("--universe-identity-hash", default="universe.identity.fixture")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_id_stability(universe_identity_hash=str(args.universe_identity_hash))
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
