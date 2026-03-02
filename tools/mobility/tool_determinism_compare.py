#!/usr/bin/env python3
"""MOB-11 deterministic compare for mobility across thread/platform variants."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402

from tools.mobility.tool_mobility_stress import _scenario_catalog, _simulate_scenario  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _parse_csv(raw: str, default_values: Sequence[str]) -> List[str]:
    rows = [str(item).strip() for item in str(raw or "").split(",")]
    out = [token for token in rows if token]
    if out:
        return sorted(set(out))
    return sorted(set(str(item).strip() for item in default_values if str(item).strip()))


def _parse_threads(raw: str) -> List[int]:
    out = []
    for token in _parse_csv(raw, ["1", "2", "4"]):
        value = _as_int(token, 0)
        if value > 0:
            out.append(int(value))
    if out:
        return sorted(set(out))
    return [1, 2, 4]


def _scenario_for_compare(*, ticks: int, dense_vehicles: int) -> dict:
    rows = _scenario_catalog(base_ticks=int(max(4, ticks)), dense_vehicles=int(max(120, dense_vehicles)))
    preferred_id = "scenario.06.mixed_fidelity_requests"
    for row in rows:
        if str(row.get("scenario_id", "")).strip() == preferred_id:
            return dict(row)
    return dict(rows[0] if rows else {})


def _run_variant(*, thread_count: int, platform_tag: str, scenario_config: dict) -> dict:
    config = dict(scenario_config or {})
    ext = dict(config.get("extensions") or {})
    ext["runtime_thread_count"] = int(max(1, int(thread_count)))
    ext["runtime_platform_tag"] = str(platform_tag)
    config["extensions"] = ext
    scenario = _simulate_scenario(config)
    metrics = dict(scenario.get("metrics") or {})
    variant = {
        "thread_count": int(max(1, int(thread_count))),
        "platform_tag": str(platform_tag),
        "scenario_id": str(scenario.get("scenario_id", "")),
        "motion_state_hash": str(metrics.get("motion_state_hash", "")),
        "event_stream_hash": str(metrics.get("event_stream_hash", "")),
        "decision_log_hash": str(metrics.get("decision_log_stability", "")),
        "occupancy_hash": str(metrics.get("occupancy_hash", "")),
        "scenario_fingerprint": str(scenario.get("deterministic_fingerprint", "")),
        "deterministic_fingerprint": "",
    }
    seed = dict(variant)
    seed["deterministic_fingerprint"] = ""
    variant["deterministic_fingerprint"] = canonical_sha256(seed)
    return variant


def run_mobility_determinism_compare(
    *,
    ticks: int,
    dense_vehicles: int,
    thread_counts: Sequence[int],
    platform_tags: Sequence[str],
) -> dict:
    scenario = _scenario_for_compare(ticks=int(ticks), dense_vehicles=int(dense_vehicles))
    variants = []
    mismatches = []
    baseline = {}
    for thread_count in sorted(set(int(max(1, _as_int(item, 1))) for item in list(thread_counts or []))):
        for platform_tag in sorted(set(str(item).strip() for item in list(platform_tags or []) if str(item).strip())):
            variant = _run_variant(
                thread_count=int(thread_count),
                platform_tag=str(platform_tag),
                scenario_config=dict(scenario),
            )
            variants.append(dict(variant))
            if not baseline:
                baseline = dict(variant)
                continue
            for field in ("motion_state_hash", "event_stream_hash", "decision_log_hash", "occupancy_hash"):
                if str(variant.get(field, "")) == str(baseline.get(field, "")):
                    continue
                mismatches.append(
                    {
                        "thread_count": int(thread_count),
                        "platform_tag": str(platform_tag),
                        "field": str(field),
                        "baseline": str(baseline.get(field, "")),
                        "actual": str(variant.get(field, "")),
                    }
                )

    report = {
        "schema_version": "1.0.0",
        "scenario_id": str(scenario.get("scenario_id", "")),
        "ticks": int(max(4, int(ticks))),
        "dense_vehicles": int(max(120, int(dense_vehicles))),
        "thread_counts": [int(item) for item in sorted(set(int(max(1, _as_int(item, 1))) for item in list(thread_counts or [])))],
        "platform_tags": sorted(set(str(item).strip() for item in list(platform_tags or []) if str(item).strip())),
        "variants": sorted(
            variants,
            key=lambda row: (
                int(_as_int(row.get("thread_count", 0), 0)),
                str(row.get("platform_tag", "")),
            ),
        ),
        "baseline_variant": dict(baseline),
        "mismatches": sorted(
            mismatches,
            key=lambda row: (
                str(row.get("field", "")),
                int(_as_int(row.get("thread_count", 0), 0)),
                str(row.get("platform_tag", "")),
            ),
        ),
        "assertions": {
            "motion_state_hashes_identical": not any(str(row.get("field", "")) == "motion_state_hash" for row in mismatches),
            "event_stream_hashes_identical": not any(str(row.get("field", "")) == "event_stream_hash" for row in mismatches),
            "decision_log_hashes_identical": not any(str(row.get("field", "")) == "decision_log_hash" for row in mismatches),
            "occupancy_hashes_identical": not any(str(row.get("field", "")) == "occupancy_hash" for row in mismatches),
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    if mismatches:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.mob.determinism_compare_mismatch",
                    "message": "mobility determinism comparison detected mismatched hashes across variants",
                    "path": "$.mismatches",
                }
            ],
            "report": report,
        }
    return {"result": "complete", "report": report}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic MOB-11 mobility compare suite.")
    parser.add_argument("--ticks", type=int, default=8)
    parser.add_argument("--dense-vehicles", type=int, default=240)
    parser.add_argument("--threads", default="1,2,4")
    parser.add_argument("--platforms", default="windows,linux,macos")
    parser.add_argument("--output", default="build/mobility/mobility_determinism_compare.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    result = run_mobility_determinism_compare(
        ticks=max(4, int(args.ticks)),
        dense_vehicles=max(120, int(args.dense_vehicles)),
        thread_counts=_parse_threads(str(args.threads)),
        platform_tags=_parse_csv(str(args.platforms), ["windows", "linux", "macos"]),
    )
    output = str(args.output).strip()
    if output:
        output_abs = os.path.normpath(os.path.abspath(output))
        _write_json(output_abs, result)
        result["output_path"] = output_abs
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
