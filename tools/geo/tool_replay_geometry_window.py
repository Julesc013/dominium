#!/usr/bin/env python3
"""Verify GEO-7 geometry edit replay determinism."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from geo import (  # noqa: E402
    build_geometry_cell_state,
    geometry_edit_policy_registry_hash,
    geometry_state_hash_surface,
)
from meta.provenance import normalize_compaction_marker_rows  # noqa: E402
from materials import create_material_batch  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import _geometry_edit_policy_registry_payload, execute_intent  # noqa: E402
from tools.xstack.testx.tests.mobility_free_testlib import (  # noqa: E402
    authority_context,
    law_profile,
    policy_context,
    seed_free_state,
)


def _cell_key(index_tuple: list[int]) -> dict:
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r3_infinite",
        "chart_id": "chart.global.r3",
        "index_tuple": list(index_tuple),
        "refinement_level": 0,
    }


def verify_geometry_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    surface = geometry_state_hash_surface(
        geometry_cell_states=state_payload.get("geometry_cell_states"),
        geometry_chunk_states=state_payload.get("geometry_chunk_states"),
        geometry_edit_events=state_payload.get("geometry_edit_events"),
    )
    recorded = {
        "geometry_edit_policy_registry_hash": str(state_payload.get("geometry_edit_policy_registry_hash", "")).strip().lower(),
        "geometry_state_hash_chain": str(state_payload.get("geometry_state_hash_chain", "")).strip().lower(),
        "geometry_cell_state_hash_chain": str(state_payload.get("geometry_cell_state_hash_chain", "")).strip().lower(),
        "geometry_chunk_state_hash_chain": str(state_payload.get("geometry_chunk_state_hash_chain", "")).strip().lower(),
        "geometry_edit_event_hash_chain": str(state_payload.get("geometry_edit_event_hash_chain", "")).strip().lower(),
        "compaction_marker_hash_chain": canonical_sha256(normalize_compaction_marker_rows(state_payload.get("compaction_markers"))),
    }
    observed = {
        "geometry_edit_policy_registry_hash": geometry_edit_policy_registry_hash(
            _geometry_edit_policy_registry_payload(None)
        ).strip().lower(),
        "geometry_state_hash_chain": str(surface.get("deterministic_fingerprint", "")).strip().lower(),
        "geometry_cell_state_hash_chain": str(surface.get("geometry_cell_state_hash", "")).strip().lower(),
        "geometry_chunk_state_hash_chain": str(surface.get("geometry_chunk_state_hash", "")).strip().lower(),
        "geometry_edit_event_hash_chain": str(surface.get("geometry_edit_event_hash_chain", "")).strip().lower(),
        "compaction_marker_hash_chain": canonical_sha256(normalize_compaction_marker_rows(state_payload.get("compaction_markers"))),
    }
    violations = []
    for key in sorted(observed.keys()):
        recorded_value = str(recorded.get(key, "")).strip().lower()
        observed_value = str(observed.get(key, "")).strip().lower()
        if recorded_value and observed_value and recorded_value != observed_value:
            violations.append("recorded {} does not match observed replay hash".format(key))
    if isinstance(expected_payload, Mapping):
        expected_surface = geometry_state_hash_surface(
            geometry_cell_states=expected_payload.get("geometry_cell_states"),
            geometry_chunk_states=expected_payload.get("geometry_chunk_states"),
            geometry_edit_events=expected_payload.get("geometry_edit_events"),
        )
        if str(expected_surface.get("deterministic_fingerprint", "")).strip().lower() != observed["geometry_state_hash_chain"]:
            violations.append("expected geometry_state_hash_chain does not match replay state")
        if str(expected_surface.get("geometry_edit_event_hash_chain", "")).strip().lower() != observed["geometry_edit_event_hash_chain"]:
            violations.append("expected geometry_edit_event_hash_chain does not match replay state")
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
    state = seed_free_state(initial_velocity_x=0)
    state["geometry_cell_states"] = [
        build_geometry_cell_state(
            geo_cell_key=_cell_key([0, 0, 0]),
            material_id="material.stone_basic",
            occupancy_fraction=1000,
        ),
        build_geometry_cell_state(
            geo_cell_key=_cell_key([1, 0, 0]),
            material_id="material.stone_basic",
            occupancy_fraction=1000,
        ),
    ]
    state["material_batches"] = [
        create_material_batch(
            material_id="material.stone_basic",
            quantity_mass_raw=600,
            origin_process_id="process.seed",
            origin_tick=0,
        )
    ]
    allowed_processes = [
        "process.geometry_remove",
        "process.geometry_add",
        "process.geometry_replace",
        "process.geometry_cut",
    ]
    law = copy.deepcopy(law_profile(allowed_processes))
    auth = copy.deepcopy(authority_context())
    policy = copy.deepcopy(policy_context())
    first = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.geo.fixture.remove",
            "process_id": "process.geometry_remove",
            "inputs": {
                "target_cell_keys": [_cell_key([0, 0, 0])],
                "volume_amount": 300,
                "roi_micro": True,
            },
        },
        law_profile=law,
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )
    second = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.geo.fixture.add",
            "process_id": "process.geometry_add",
            "inputs": {
                "target_cell_keys": [_cell_key([0, 0, 0])],
                "volume_amount": 100,
                "material_id": "material.stone_basic",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    report = verify_geometry_replay_window(state_payload=state)
    return {
        "process_results": [dict(first), dict(second)],
        "replay_report": dict(report),
        "geometry_state_hash_chain": str(state.get("geometry_state_hash_chain", "")).strip(),
        "geometry_edit_event_hash_chain": str(state.get("geometry_edit_event_hash_chain", "")).strip(),
        "run_hash": canonical_sha256(
            {
                "process_results": [dict(first), dict(second)],
                "replay_report": dict(report),
            }
        ),
    }


def verify_geometry_window_fixture() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    replay_report = dict(first.get("replay_report") or {})
    report = {
        "result": "complete" if stable and str(replay_report.get("result", "")) == "complete" else "violation",
        "replay_report": replay_report,
        "geometry_state_hash_chain": str(first.get("geometry_state_hash_chain", "")),
        "geometry_edit_event_hash_chain": str(first.get("geometry_edit_event_hash_chain", "")),
        "run_hash": str(first.get("run_hash", "")),
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-7 geometry replay determinism.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_geometry_window_fixture()
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
