#!/usr/bin/env python3
"""Verify MW-1 star-system instantiation replay determinism."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.testx.tests.geo8_testlib import run_worldgen_process, seed_worldgen_state, worldgen_request_row  # noqa: E402
from geo import worldgen_cache_clear  # noqa: E402
from worldgen.mw import star_system_artifact_hash_chain  # noqa: E402


def _run_once() -> dict:
    worldgen_cache_clear()
    state = seed_worldgen_state()
    result = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="mw1.system_instantiation.fixture",
            index_tuple=[800, 0, 0],
            refinement_level=1,
            reason="query",
        ),
    )
    worldgen_result_rows = list(state.get("worldgen_results") or [])
    worldgen_result = dict(worldgen_result_rows[0]) if worldgen_result_rows else {}
    artifact_rows = [dict(row) for row in list(state.get("worldgen_star_system_artifacts") or []) if isinstance(row, dict)]
    report = {
        "process_result": dict(result),
        "worldgen_result_id": str(worldgen_result.get("result_id", "")).strip(),
        "star_system_artifact_ids": [
            str(row.get("object_id", "")).strip()
            for row in sorted(artifact_rows, key=lambda item: str(item.get("object_id", "")))
        ],
        "star_system_seed_values": [
            str(row.get("system_seed_value", "")).strip()
            for row in sorted(artifact_rows, key=lambda item: str(item.get("object_id", "")))
        ],
        "star_system_artifact_hash_chain": star_system_artifact_hash_chain(artifact_rows),
        "worldgen_result_hash_chain": str(state.get("worldgen_result_hash_chain", "")).strip(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_system_instantiation_replay() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "first_run": first,
        "second_run": second,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify MW-1 star-system instantiation replay determinism.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_system_instantiation_replay()
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
