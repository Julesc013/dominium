#!/usr/bin/env python3
"""Run deterministic PROV-0 provenance compaction stress scenarios."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, Iterable, List, Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from meta.provenance import (  # noqa: E402
    compact_provenance_window,
    verify_replay_from_compaction_anchor,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, dict):
        return {}, "json root must be an object"
    return payload, ""


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _classification_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = list((dict(payload.get("record") or {})).get("provenance_classifications") or [])
    if not rows:
        rows = list(payload.get("provenance_classifications") or [])
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _empty_shard_state(shard_id: str) -> dict:
    return {
        "energy_ledger_entries": [],
        "boundary_flux_events": [],
        "time_adjust_events": [],
        "fault_events": [],
        "exception_events": [],
        "leak_events": [],
        "burst_events": [],
        "relief_events": [],
        "branch_events": [],
        "compaction_markers": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
        "explain_artifact_rows": [],
        "inspection_snapshot_rows": [],
        "model_evaluation_results": [],
        "derived_summary_rows": [],
        "derived_statistics_rows": [],
        "provenance_compaction_summaries": [],
        "time_branches": [],
        "control_proof_bundles": [],
        "extensions": {"shard_id": str(shard_id)},
    }


def _append_tick_rows(
    *,
    state: dict,
    shard_id: str,
    tick: int,
    events_per_tick: int,
) -> None:
    tick_value = int(max(0, _as_int(tick, 0)))
    for index in range(0, int(max(1, events_per_tick))):
        suffix = "{}.{}.{}".format(str(shard_id), tick_value, index)
        state["energy_ledger_entries"].append(
            {
                "entry_id": "entry.energy.{}".format(suffix),
                "tick": tick_value,
                "source_id": "assembly.{}".format(shard_id),
                "transformation_id": "transform.electrical_to_thermal" if (index % 2 == 0) else "transform.kinetic_to_thermal",
                "input_values": {"quantity.energy_electrical": 300 + index * 5},
                "output_values": {"quantity.energy_thermal": 300 + index * 5},
                "energy_total_delta": 0,
                "extensions": {"domain_hint": "elec" if (index % 2 == 0) else "fluid"},
            }
        )
        state["boundary_flux_events"].append(
            {
                "flux_id": "flux.{}".format(suffix),
                "tick": tick_value,
                "quantity_id": "quantity.energy_thermal",
                "value": 18 + index,
                "direction": "in",
                "reason_code": "stress.boundary_flux",
                "extensions": {"domain_hint": "therm"},
            }
        )
        state["fault_events"].append(
            {
                "event_id": "fault.{}".format(suffix),
                "tick": tick_value,
                "target_id": "assembly.{}".format(shard_id),
                "reason_code": "stress.fault.stub",
                "extensions": {"domain_hint": "fluid" if (index % 3 == 0) else "elec"},
            }
        )
        state["info_artifact_rows"].append(
            {
                "artifact_id": "artifact.explain.{}".format(suffix),
                "artifact_type_id": "artifact.explain",
                "tick": tick_value,
                "extensions": {},
            }
        )
        state["knowledge_artifacts"].append(
            {
                "artifact_id": "artifact.explain.{}".format(suffix),
                "artifact_type_id": "artifact.explain",
                "tick": tick_value,
                "extensions": {},
            }
        )
        state["explain_artifact_rows"].append(
            {
                "explain_id": "explain.{}".format(suffix),
                "tick": tick_value,
                "cause_chain": ["stress.synthetic", "tick.{}".format(tick_value)],
                "extensions": {},
            }
        )
        state["inspection_snapshot_rows"].append(
            {
                "snapshot_id": "snapshot.{}".format(suffix),
                "tick": tick_value,
                "target_id": "network.{}".format(shard_id),
                "extensions": {"domain_hint": "fluid"},
            }
        )
        state["model_evaluation_results"].append(
            {
                "model_id": "model.stress.synthetic",
                "tick": tick_value,
                "deterministic_fingerprint": canonical_sha256({"shard_id": shard_id, "tick": tick_value, "index": index}),
                "extensions": {},
            }
        )
    state["time_adjust_events"].append(
        {
            "adjust_id": "time.adjust.{}.{}".format(str(shard_id), tick_value),
            "tick": tick_value,
            "target_id": "clock.{}".format(shard_id),
            "previous_domain_time": tick_value * 10,
            "new_domain_time": (tick_value * 10) + 1,
            "adjustment_delta": 1,
            "originating_receipt_id": "receipt.{}.{}".format(shard_id, tick_value),
            "extensions": {"domain_hint": "time"},
        }
    )


def _count_rows(state: Mapping[str, object], keys: Iterable[str]) -> int:
    return int(
        sum(
            len([row for row in list(state.get(key) or []) if isinstance(row, Mapping)])
            for key in keys
        )
    )


_CANONICAL_KEYS = (
    "energy_ledger_entries",
    "boundary_flux_events",
    "time_adjust_events",
    "fault_events",
    "exception_events",
    "leak_events",
    "burst_events",
    "relief_events",
    "branch_events",
    "compaction_markers",
)

_DERIVED_KEYS = (
    "info_artifact_rows",
    "knowledge_artifacts",
    "explain_artifact_rows",
    "inspection_snapshot_rows",
    "model_evaluation_results",
    "derived_summary_rows",
    "derived_statistics_rows",
    "provenance_compaction_summaries",
)


def _deterministic_anchor_index(*, shard_id: str, marker_count: int, seed: int) -> int:
    if int(marker_count) <= 0:
        return 0
    digest = canonical_sha256({"shard_id": str(shard_id), "seed": int(seed)})
    return int(int(digest[:16], 16) % int(marker_count))


def run_provenance_stress(
    *,
    classification_rows: List[dict],
    shard_count: int,
    tick_count: int,
    events_per_tick: int,
    compact_every_ticks: int,
    deterministic_seed: int,
) -> dict:
    shards = ["shard.{:03d}".format(index) for index in range(0, int(max(1, shard_count)))]
    states: Dict[str, dict] = dict((shard_id, _empty_shard_state(shard_id)) for shard_id in shards)

    generated_derived_rows = 0
    removed_derived_rows = 0
    total_rows_before_compaction = 0
    total_rows_after_compaction = 0

    for tick in range(0, int(max(1, tick_count))):
        for shard_id in sorted(shards):
            state = states[shard_id]
            _append_tick_rows(
                state=state,
                shard_id=shard_id,
                tick=tick,
                events_per_tick=int(max(1, events_per_tick)),
            )
            generated_derived_rows += int(max(1, events_per_tick)) * 5
            if ((tick + 1) % int(max(1, compact_every_ticks))) != 0:
                continue

            before = _count_rows(state, _DERIVED_KEYS)
            start_tick = int(max(0, tick - int(max(1, compact_every_ticks)) + 1))
            compacted = compact_provenance_window(
                state_payload=state,
                classification_rows=classification_rows,
                shard_id=shard_id,
                start_tick=start_tick,
                end_tick=int(tick),
            )
            if str(compacted.get("result", "")) != "complete":
                return {
                    "result": "refused",
                    "reason_code": "refusal.provenance.compaction_failed",
                    "message": "compaction failed for shard '{}' tick {}".format(shard_id, tick),
                    "details": compacted,
                }
            states[shard_id] = dict(compacted.get("state") or {})
            after = _count_rows(states[shard_id], _DERIVED_KEYS)
            removed_derived_rows += int(max(0, before - after))

        total_rows_before_compaction += int(
            sum(_count_rows(states[shard_id], _CANONICAL_KEYS + _DERIVED_KEYS) for shard_id in sorted(shards))
        )
        total_rows_after_compaction += int(
            sum(_count_rows(states[shard_id], _CANONICAL_KEYS + _DERIVED_KEYS) for shard_id in sorted(shards))
        )

    replay_reports: List[dict] = []
    shard_digests: Dict[str, str] = {}
    for shard_id in sorted(shards):
        state = states[shard_id]
        marker_rows = [dict(row) for row in list(state.get("compaction_markers") or []) if isinstance(row, Mapping)]
        if not marker_rows:
            return {
                "result": "refused",
                "reason_code": "refusal.provenance.no_compaction_markers",
                "message": "no compaction markers were generated for shard '{}'".format(shard_id),
            }
        marker_rows = sorted(
            marker_rows,
            key=lambda row: (
                int(max(0, _as_int(row.get("start_tick", 0), 0))),
                str(row.get("marker_id", "")),
            ),
        )
        index = _deterministic_anchor_index(
            shard_id=shard_id,
            marker_count=len(marker_rows),
            seed=deterministic_seed,
        )
        marker = dict(marker_rows[index])
        verify = verify_replay_from_compaction_anchor(
            state_payload=state,
            marker_id=str(marker.get("marker_id", "")),
        )
        if str(verify.get("result", "")) != "complete":
            return {
                "result": "refused",
                "reason_code": "refusal.provenance.anchor_replay_failed",
                "message": "replay-from-anchor failed for shard '{}'".format(shard_id),
                "details": verify,
            }
        replay_reports.append(
            {
                "shard_id": shard_id,
                "marker_id": str(marker.get("marker_id", "")),
                "marker_end_tick": int(max(0, _as_int(marker.get("end_tick", 0), 0))),
                "replay_hash": str(verify.get("replay_hash", "")),
                "compaction_marker_hash_chain": str(verify.get("compaction_marker_hash_chain", "")),
            }
        )
        shard_digests[shard_id] = canonical_sha256(state)

    storage_growth_permille = int(
        (
            (total_rows_after_compaction - total_rows_before_compaction) * 1000
            // max(1, total_rows_before_compaction)
        )
    )
    compaction_effectiveness_permille = int(
        (removed_derived_rows * 1000) // max(1, generated_derived_rows)
    )
    replay_cost_units = int(
        sum(
            int(max(0, _as_int(tick_count, 0)) - int(max(0, _as_int(row.get("marker_end_tick", 0), 0))))
            for row in replay_reports
        )
    )
    metrics = {
        "storage_growth_permille": int(storage_growth_permille),
        "compaction_effectiveness_permille": int(compaction_effectiveness_permille),
        "generated_derived_rows": int(generated_derived_rows),
        "removed_derived_rows": int(removed_derived_rows),
        "replay_cost_units": int(replay_cost_units),
    }
    report = {
        "schema_version": "1.0.0",
        "result": "complete",
        "shard_count": int(len(shards)),
        "tick_count": int(max(1, tick_count)),
        "events_per_tick": int(max(1, events_per_tick)),
        "compact_every_ticks": int(max(1, compact_every_ticks)),
        "deterministic_seed": int(deterministic_seed),
        "metrics": metrics,
        "replay_reports": sorted(replay_reports, key=lambda row: str(row.get("shard_id", ""))),
        "shard_state_hashes": dict((key, shard_digests[key]) for key in sorted(shard_digests.keys())),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic provenance stress+compaction validation.")
    parser.add_argument(
        "--classification-registry",
        default=os.path.join("data", "registries", "provenance_classification_registry.json"),
    )
    parser.add_argument("--shards", type=int, default=4)
    parser.add_argument("--ticks", type=int, default=128)
    parser.add_argument("--events-per-tick", type=int, default=8)
    parser.add_argument("--compact-every-ticks", type=int, default=16)
    parser.add_argument("--seed", type=int, default=9017)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    registry_path = os.path.normpath(os.path.abspath(str(args.classification_registry)))
    if not os.path.isabs(registry_path):
        registry_path = os.path.normpath(os.path.join(REPO_ROOT_HINT, registry_path))
    payload, error = _read_json(registry_path)
    if error:
        print(
            json.dumps(
                {
                    "result": "refused",
                    "reason_code": "refusal.provenance.invalid_classification_registry",
                    "message": "invalid provenance classification registry: {}".format(error),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    classification_rows = _classification_rows(payload)
    if not classification_rows:
        print(
            json.dumps(
                {
                    "result": "refused",
                    "reason_code": "refusal.provenance.empty_classification_registry",
                    "message": "provenance classification registry has no rows",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    first = run_provenance_stress(
        classification_rows=classification_rows,
        shard_count=int(max(1, _as_int(args.shards, 4))),
        tick_count=int(max(1, _as_int(args.ticks, 128))),
        events_per_tick=int(max(1, _as_int(args.events_per_tick, 8))),
        compact_every_ticks=int(max(1, _as_int(args.compact_every_ticks, 16))),
        deterministic_seed=int(_as_int(args.seed, 9017)),
    )
    second = run_provenance_stress(
        classification_rows=copy.deepcopy(classification_rows),
        shard_count=int(max(1, _as_int(args.shards, 4))),
        tick_count=int(max(1, _as_int(args.ticks, 128))),
        events_per_tick=int(max(1, _as_int(args.events_per_tick, 8))),
        compact_every_ticks=int(max(1, _as_int(args.compact_every_ticks, 16))),
        deterministic_seed=int(_as_int(args.seed, 9017)),
    )
    if str(first.get("result", "")) != "complete":
        print(json.dumps(first, indent=2, sort_keys=True))
        return 1
    if str(second.get("result", "")) != "complete":
        print(json.dumps(second, indent=2, sort_keys=True))
        return 1
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        print(
            json.dumps(
                {
                    "result": "violation",
                    "reason_code": "refusal.provenance.stress_nondeterministic",
                    "message": "stress fingerprints drifted across equivalent runs",
                    "first_fingerprint": str(first.get("deterministic_fingerprint", "")),
                    "second_fingerprint": str(second.get("deterministic_fingerprint", "")),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    output_path = str(args.output or "").strip()
    if output_path:
        abs_output = os.path.normpath(os.path.abspath(output_path))
        _write_json(abs_output, first)
    print(json.dumps(first, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
