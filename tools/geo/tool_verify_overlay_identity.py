#!/usr/bin/env python3
"""Verify GEO-10 overlay application preserves stable object identities."""

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

from tools.geo.geo10_stress_runtime import _as_map, _suite_worldgen_and_overlay, load_geo_stress_scenario  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _selected_suites(scenario: Mapping[str, object], suite_id: str) -> list[dict]:
    rows = [dict(row) for row in list(scenario.get("topology_suites") or []) if isinstance(row, Mapping)]
    token = str(suite_id or "").strip()
    if not token:
        return sorted(rows, key=lambda row: str(row.get("suite_id", "")))
    return [dict(row) for row in rows if str(row.get("suite_id", "")).strip() == token]


def _identity_snapshot(*, scenario: Mapping[str, object], suite: Mapping[str, object]) -> dict:
    overlay_data = _suite_worldgen_and_overlay(suite=suite, scenario=scenario)
    base_ids = sorted(
        str(_as_map(row).get("object_id", "")).strip()
        for row in list(overlay_data.get("base_objects") or [])
        if str(_as_map(row).get("object_id", "")).strip()
    )
    merged_ids = sorted(
        str(_as_map(row).get("object_id", "")).strip()
        for row in list(_as_map(overlay_data.get("merge_result")).get("effective_object_views") or [])
        if str(_as_map(row).get("object_id", "")).strip()
    )
    snapshot = {
        "suite_id": str(suite.get("suite_id", "")).strip(),
        "stable_identity_under_overlay": bool(overlay_data.get("stable_identity_under_overlay")),
        "base_ids": base_ids,
        "merged_ids": merged_ids,
        "origin_report": dict(_as_map(overlay_data.get("origin_report"))),
        "overlay_manifest_hash": str(_as_map(overlay_data.get("overlay_surface")).get("overlay_manifest_hash", "")).strip(),
        "overlay_merge_result_hash_chain": str(
            _as_map(overlay_data.get("overlay_surface")).get("overlay_merge_result_hash_chain", "")
        ).strip(),
        "deterministic_fingerprint": "",
    }
    snapshot["deterministic_fingerprint"] = canonical_sha256(dict(snapshot, deterministic_fingerprint=""))
    return snapshot


def _run_once(*, scenario: Mapping[str, object], suite_id: str) -> dict:
    suite_rows = _selected_suites(scenario, suite_id)
    snapshots = [_identity_snapshot(scenario=scenario, suite=row) for row in suite_rows]
    return {
        "scenario_id": str(scenario.get("scenario_id", "")).strip(),
        "suite_snapshots": snapshots,
        "run_hash": canonical_sha256({"scenario_id": str(scenario.get("scenario_id", "")).strip(), "suite_snapshots": snapshots}),
    }


def verify_overlay_identity(*, scenario: Mapping[str, object], suite_id: str = "") -> dict:
    first = _run_once(scenario=scenario, suite_id=suite_id)
    second = _run_once(scenario=scenario, suite_id=suite_id)
    stable = first == second
    snapshots = [dict(row) for row in list(first.get("suite_snapshots") or []) if isinstance(row, Mapping)]
    report = {
        "result": "complete"
        if stable and all(bool(row.get("stable_identity_under_overlay", False)) for row in snapshots)
        else "violation",
        "scenario_id": str(first.get("scenario_id", "")),
        "suite_snapshots": snapshots,
        "stable_across_repeated_runs": bool(stable),
        "run_hash": str(first.get("run_hash", "")),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-10 overlay identity stability.")
    parser.add_argument("--scenario", default="build/geo/geo10_stress_scenario.json")
    parser.add_argument("--suite-id", default="")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    scenario = load_geo_stress_scenario(str(args.scenario or "").strip())
    report = verify_overlay_identity(scenario=scenario, suite_id=str(args.suite_id or "").strip())
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
