#!/usr/bin/env python3
"""Verify GEO-8 worldgen replay determinism for canonical cell requests."""

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

from src.geo import generator_version_registry_hash, realism_profile_registry_hash, worldgen_cache_clear, worldgen_result_proof_surface  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import (  # noqa: E402
    _generator_version_registry_payload,
    _realism_profile_registry_payload,
)
from tools.xstack.testx.tests.geo8_testlib import run_worldgen_process, seed_worldgen_state, worldgen_request_row  # noqa: E402


def verify_worldgen_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    surface = worldgen_result_proof_surface(
        worldgen_requests=state_payload.get("worldgen_requests"),
        worldgen_results=state_payload.get("worldgen_results"),
        worldgen_spawned_objects=state_payload.get("worldgen_spawned_objects"),
    )
    recorded = {
        "generator_version_registry_hash": str(state_payload.get("generator_version_registry_hash", "")).strip().lower(),
        "realism_profile_registry_hash": str(state_payload.get("realism_profile_registry_hash", "")).strip().lower(),
        "worldgen_request_hash_chain": str(state_payload.get("worldgen_request_hash_chain", "")).strip().lower(),
        "worldgen_result_hash_chain": str(state_payload.get("worldgen_result_hash_chain", "")).strip().lower(),
        "worldgen_spawned_object_hash_chain": str(state_payload.get("worldgen_spawned_object_hash_chain", "")).strip().lower(),
    }
    observed = {
        "generator_version_registry_hash": generator_version_registry_hash(
            _generator_version_registry_payload(None)
        ).strip().lower(),
        "realism_profile_registry_hash": realism_profile_registry_hash(
            _realism_profile_registry_payload(None)
        ).strip().lower(),
        "worldgen_request_hash_chain": str(surface.get("worldgen_request_hash_chain", "")).strip().lower(),
        "worldgen_result_hash_chain": str(surface.get("worldgen_result_hash_chain", "")).strip().lower(),
        "worldgen_spawned_object_hash_chain": str(surface.get("worldgen_spawned_object_hash_chain", "")).strip().lower(),
    }
    violations = []
    for key in sorted(observed.keys()):
        recorded_value = str(recorded.get(key, "")).strip().lower()
        observed_value = str(observed.get(key, "")).strip().lower()
        if recorded_value and observed_value and recorded_value != observed_value:
            violations.append("recorded {} does not match observed replay hash".format(key))
    if isinstance(expected_payload, Mapping):
        expected_surface = worldgen_result_proof_surface(
            worldgen_requests=expected_payload.get("worldgen_requests"),
            worldgen_results=expected_payload.get("worldgen_results"),
            worldgen_spawned_objects=expected_payload.get("worldgen_spawned_objects"),
        )
        if str(expected_surface.get("worldgen_result_hash_chain", "")).strip().lower() != observed["worldgen_result_hash_chain"]:
            violations.append("expected worldgen_result_hash_chain does not match replay state")
    report = {
        "result": "violation" if violations else "complete",
        "recorded": recorded,
        "observed": observed,
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _run_once() -> dict:
    worldgen_cache_clear()
    state = seed_worldgen_state()
    first = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="worldgen.fixture.cell.primary",
            index_tuple=[12, -4, 7],
            refinement_level=3,
            reason="query",
        ),
    )
    second = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="worldgen.fixture.cell.secondary",
            index_tuple=[12, -4, 7],
            refinement_level=3,
            reason="query",
        ),
    )
    report = verify_worldgen_replay_window(state_payload=state)
    return {
        "process_results": [dict(first), dict(second)],
        "replay_report": dict(report),
        "worldgen_request_hash_chain": str(state.get("worldgen_request_hash_chain", "")).strip(),
        "worldgen_result_hash_chain": str(state.get("worldgen_result_hash_chain", "")).strip(),
        "worldgen_spawned_object_hash_chain": str(state.get("worldgen_spawned_object_hash_chain", "")).strip(),
        "run_hash": canonical_sha256(
            {
                "process_results": [dict(first), dict(second)],
                "replay_report": dict(report),
            }
        ),
    }


def verify_worldgen_cell_replay() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    replay_report = dict(first.get("replay_report") or {})
    report = {
        "result": "complete" if stable and str(replay_report.get("result", "")) == "complete" else "violation",
        "replay_report": replay_report,
        "worldgen_request_hash_chain": str(first.get("worldgen_request_hash_chain", "")),
        "worldgen_result_hash_chain": str(first.get("worldgen_result_hash_chain", "")),
        "worldgen_spawned_object_hash_chain": str(first.get("worldgen_spawned_object_hash_chain", "")),
        "run_hash": str(first.get("run_hash", "")),
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-8 worldgen replay determinism.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_worldgen_cell_replay()
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
