#!/usr/bin/env python3
"""SYS-8 deterministic stress scenario generator."""

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

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


_SYSTEM_KINDS = (
    "engine",
    "pump",
    "generator",
    "heat_exchanger",
)

_KIND_MACRO_MODEL_SET = {
    "engine": "macro.engine_stub",
    "pump": "macro.pump_stub",
    "generator": "macro.generator_stub",
    "heat_exchanger": "macro.heat_exchanger_stub",
}

_KIND_RELIABILITY_PROFILE = {
    "engine": "reliability.engine_basic",
    "pump": "reliability.pump_basic",
    "generator": "reliability.power_system_basic",
    "heat_exchanger": "reliability.pressure_system_basic",
}

_KIND_DOMAIN_MIX = {
    "engine": ["ELEC", "THERM", "FLUID", "CHEM", "POLL"],
    "pump": ["ELEC", "FLUID", "POLL"],
    "generator": ["ELEC", "THERM", "CHEM", "POLL"],
    "heat_exchanger": ["THERM", "FLUID", "POLL"],
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _pick(seed: int, stream: str, index: int, modulo: int, *, offset: int = 0) -> int:
    mod = int(modulo)
    if mod <= 0:
        return int(offset)
    digest = canonical_sha256(
        {
            "seed": int(seed),
            "stream": str(stream),
            "index": int(index),
            "modulo": int(mod),
        }
    )
    return int(int(offset) + (int(digest[:12], 16) % int(mod)))


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _seed_rows() -> Tuple[dict, dict, List[dict], List[dict]]:
    if REPO_ROOT_HINT not in sys.path:
        sys.path.insert(0, REPO_ROOT_HINT)
    from tools.xstack.testx.tests.sys0_testlib import cloned_state  # noqa: E402

    seed = copy.deepcopy(cloned_state())
    system_seed = dict((seed.get("system_rows") or [{}])[0] or {})
    interface_seed = dict((seed.get("system_interface_signature_rows") or [{}])[0] or {})
    invariant_rows = [
        dict(row)
        for row in list(seed.get("system_boundary_invariant_rows") or [])
        if isinstance(row, Mapping)
    ]
    assembly_seed_rows = [
        dict(row)
        for row in list(seed.get("assembly_rows") or [])
        if isinstance(row, Mapping)
    ]
    return system_seed, interface_seed, invariant_rows, assembly_seed_rows


def _assembly_rows_for_system(kind: str, ordinal: int) -> List[dict]:
    root = "assembly.{}.root.{}".format(kind, str(ordinal).zfill(5))
    aux_a = "assembly.{}.auxa.{}".format(kind, str(ordinal).zfill(5))
    aux_b = "assembly.{}.auxb.{}".format(kind, str(ordinal).zfill(5))
    return [
        {
            "schema_version": "1.0.0",
            "assembly_id": root,
            "assembly_type_id": "assembly.{}.root".format(kind),
            "deterministic_fingerprint": "",
            "extensions": {"system_kind": kind, "role": "root"},
        },
        {
            "schema_version": "1.0.0",
            "assembly_id": aux_a,
            "assembly_type_id": "assembly.{}.module".format(kind),
            "deterministic_fingerprint": "",
            "extensions": {"system_kind": kind, "role": "module_a"},
        },
        {
            "schema_version": "1.0.0",
            "assembly_id": aux_b,
            "assembly_type_id": "assembly.{}.module".format(kind),
            "deterministic_fingerprint": "",
            "extensions": {"system_kind": kind, "role": "module_b"},
        },
    ]


def _state_vector_for_macro(*, system_id: str, tick: int, assembly_rows: List[dict]) -> Tuple[str, str, dict]:
    serialized = {
        "schema_version": "1.0.0",
        "encoding": "canonical_json.v1",
        "system_id": str(system_id),
        "captured_tick": int(max(0, _as_int(tick, 0))),
        "assembly_rows": [dict(row) for row in assembly_rows],
    }
    anchor = canonical_sha256(serialized)
    state_vector_id = "statevec.system.{}".format(
        canonical_sha256({"system_id": str(system_id), "tick": int(max(0, _as_int(tick, 0)))})[:16]
    )
    row = {
        "schema_version": "1.0.0",
        "state_vector_id": state_vector_id,
        "system_id": str(system_id),
        "serialized_internal_state": dict(serialized),
        "deterministic_fingerprint": "",
        "extensions": {
            "source_process_id": "process.system_collapse",
            "captured_assembly_count": int(len(assembly_rows)),
            "anchor_hash": str(anchor),
        },
    }
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return state_vector_id, anchor, row


def _system_rows(
    *,
    seed: int,
    tick_horizon: int,
    system_count: int,
    nested_size: int,
    shard_count: int,
) -> dict:
    system_seed, interface_seed, invariant_rows, _assembly_seed_rows = _seed_rows()
    del _assembly_seed_rows
    systems: List[dict] = []
    interfaces: List[dict] = []
    assemblies: List[dict] = []
    capsules: List[dict] = []
    state_vectors: List[dict] = []
    nested_plants: List[dict] = []
    shard_map: Dict[str, str] = {}

    macro_ratio_permille = 750
    nested_group = int(max(2, _as_int(nested_size, 16)))
    total = int(max(1, _as_int(system_count, 512)))
    shard_total = int(max(1, _as_int(shard_count, 4)))

    all_system_ids: List[str] = []
    for idx in range(total):
        ordinal = int(idx + 1)
        kind = _SYSTEM_KINDS[idx % len(_SYSTEM_KINDS)]
        system_id = "system.stress.{}.{}".format(kind, str(ordinal).zfill(5))
        all_system_ids.append(system_id)

        assembly_rows = _assembly_rows_for_system(kind, ordinal)
        assembly_ids = [str(row.get("assembly_id", "")).strip() for row in assembly_rows if str(row.get("assembly_id", "")).strip()]
        root_assembly_id = str(assembly_ids[0]) if assembly_ids else ""
        interface_id = "iface.{}".format(system_id)
        capsule_id = "capsule.{}".format(system_id.replace(".", "_"))

        macro_model_set_id = str(_KIND_MACRO_MODEL_SET.get(kind, "macro.engine_stub"))
        reliability_profile_id = str(_KIND_RELIABILITY_PROFILE.get(kind, "reliability.engine_basic"))
        hazard_base = int(150 + _pick(seed, "sys.hazard.base", idx, 220))
        current_tier = "macro" if _pick(seed, "sys.start_tier", idx, 1000) < macro_ratio_permille else "micro"
        if idx < max(2, total // 8):
            current_tier = "micro"

        sys_row = dict(system_seed)
        sys_row["system_id"] = system_id
        sys_row["root_assembly_id"] = root_assembly_id
        sys_row["assembly_ids"] = list(assembly_ids)
        sys_row["interface_signature_id"] = interface_id
        sys_row["boundary_invariant_ids"] = [
            "invariant.mass_conserved",
            "invariant.energy_conserved",
            "invariant.pollutant_accounted",
        ]
        sys_row["tier_contract_id"] = "tier.system.default"
        sys_row["current_tier"] = current_tier
        sys_row["active_capsule_id"] = capsule_id if current_tier == "macro" else ""
        sys_ext = _as_map(sys_row.get("extensions"))
        sys_ext["macro_model_set_id"] = macro_model_set_id
        sys_ext["model_error_bounds_ref"] = "tol.strict"
        sys_ext["reliability_profile_id"] = reliability_profile_id
        sys_ext["domain_mix"] = list(_KIND_DOMAIN_MIX.get(kind, []))
        sys_ext["hazard_levels"] = {
            "hazard.thermal.overheat": int(hazard_base),
            "hazard.control.loss": int(max(0, hazard_base - 50)),
        }
        sys_ext["unresolved_hazard_count"] = 0
        sys_ext["pending_internal_event_count"] = 0
        sys_ext["open_scheduled_task_count"] = 0
        sys_ext["open_branch_dependency_count"] = 0
        sys_row["extensions"] = sys_ext
        sys_row["deterministic_fingerprint"] = canonical_sha256(dict(sys_row, deterministic_fingerprint=""))
        systems.append(sys_row)

        iface = dict(interface_seed)
        iface["system_id"] = system_id
        iface["interface_signature_id"] = interface_id
        iface["signal_channels"] = [
            {
                "channel_id": "sig.{}.control".format(system_id.replace(".", "_")),
                "direction": "bidir",
            }
        ]
        iface["signal_descriptors"] = [
            {
                "channel_type_id": "channel.wired_basic",
                "capacity": 1024,
                "delay": 1,
                "access_policy_id": "access.system.default",
            }
        ]
        iface["deterministic_fingerprint"] = canonical_sha256(dict(iface, deterministic_fingerprint=""))
        interfaces.append(iface)

        shard_map[system_id] = "shard.{}".format(str(_pick(seed, "sys.shard", idx, shard_total)).zfill(2))

        if current_tier == "macro":
            state_vector_id, anchor_hash, state_vector_row = _state_vector_for_macro(
                system_id=system_id,
                tick=0,
                assembly_rows=assembly_rows,
            )
            state_vectors.append(state_vector_row)
            capsule_row = {
                "schema_version": "1.1.0",
                "capsule_id": capsule_id,
                "system_id": system_id,
                "interface_signature_id": interface_id,
                "macro_model_set_id": macro_model_set_id,
                "model_error_bounds_ref": "tol.strict",
                "macro_model_bindings": [],
                "internal_state_vector": {
                    "state_vector_id": state_vector_id,
                    "anchor_hash": anchor_hash,
                },
                "provenance_anchor_hash": anchor_hash,
                "tier_mode": "macro",
                "deterministic_fingerprint": "",
                "extensions": {
                    "source_process_id": "process.system_collapse",
                    "region_id": "region.sys.stress.{}".format(str((idx // nested_group) + 1).zfill(3)),
                    "fail_safe_on_forced_expand": True,
                    "hazard_level": int(max(0, hazard_base - 80)),
                    "max_error_estimate": 8,
                    "boundary_invariant_ids": [
                        "invariant.mass_conserved",
                        "invariant.energy_conserved",
                        "invariant.pollutant_accounted",
                    ],
                    "flow_channel_by_port": {},
                    "signal_channel_by_name": {"default": "sig.{}.control".format(system_id.replace(".", "_"))},
                },
            }
            capsule_row["deterministic_fingerprint"] = canonical_sha256(dict(capsule_row, deterministic_fingerprint=""))
            capsules.append(capsule_row)
            placeholder_id = "assembly.system_capsule_placeholder.{}".format(system_id)
            assemblies.append(
                {
                    "schema_version": "1.0.0",
                    "assembly_id": placeholder_id,
                    "assembly_type_id": "assembly.system.capsule_placeholder",
                    "deterministic_fingerprint": canonical_sha256(
                        {"system_id": system_id, "placeholder": True, "capsule_id": capsule_id}
                    ),
                    "extensions": {
                        "source_process_id": "process.system_collapse",
                        "system_id": system_id,
                        "capsule_id": capsule_id,
                        "interface_signature_id": interface_id,
                    },
                }
            )
        else:
            for row in assembly_rows:
                row = dict(row)
                row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
                assemblies.append(row)

    plant_count = max(1, (total + nested_group - 1) // nested_group)
    for plant_idx in range(plant_count):
        start = plant_idx * nested_group
        end = min(total, start + nested_group)
        children = sorted(all_system_ids[start:end])
        plant_id = "system.stress.plant.{}".format(str(plant_idx + 1).zfill(4))
        nested_plants.append(
            {
                "plant_system_id": plant_id,
                "child_system_ids": list(children),
                "tier_contract_id": "tier.system.default",
                "macro_model_set_id": "macro.generator_stub",
                "boundary_invariant_ids": [
                    "invariant.mass_conserved",
                    "invariant.energy_conserved",
                    "invariant.pollutant_accounted",
                ],
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "plant_system_id": plant_id,
                        "child_system_ids": list(children),
                    }
                ),
            }
        )

    hazard_events: List[dict] = []
    for tick in range(1, int(max(2, tick_horizon)), 3):
        escalations = max(1, total // 20)
        for event_idx in range(escalations):
            system_id = all_system_ids[_pick(seed, "hazard.system", tick * 100 + event_idx, len(all_system_ids))]
            hazard_id = "hazard.thermal.overheat" if ((tick + event_idx) % 2 == 0) else "hazard.control.loss"
            delta = int(80 + _pick(seed, "hazard.delta", tick * 100 + event_idx, 210))
            hazard_events.append(
                {
                    "event_id": "event.system.hazard_escalation.{}".format(
                        canonical_sha256(
                            {
                                "tick": int(tick),
                                "system_id": str(system_id),
                                "hazard_id": hazard_id,
                                "event_idx": int(event_idx),
                            }
                        )[:16]
                    ),
                    "tick": int(tick),
                    "system_id": str(system_id),
                    "hazard_id": str(hazard_id),
                    "hazard_delta": int(delta),
                    "rng_stream_name": "rng.sys8.hazard_escalation",
                    "profile_gated": True,
                }
            )
    hazard_events = sorted(
        (dict(row) for row in hazard_events),
        key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("system_id", "")), str(row.get("event_id", ""))),
    )

    return {
        "system_rows": [dict(row) for row in sorted(systems, key=lambda row: str(row.get("system_id", "")))],
        "system_interface_signature_rows": [dict(row) for row in sorted(interfaces, key=lambda row: str(row.get("system_id", "")))],
        "system_boundary_invariant_rows": [dict(row) for row in sorted(invariant_rows, key=lambda row: str(row.get("invariant_id", "")))],
        "system_macro_capsule_rows": [dict(row) for row in sorted(capsules, key=lambda row: str(row.get("system_id", "")))],
        "system_state_vector_rows": [dict(row) for row in sorted(state_vectors, key=lambda row: str(row.get("system_id", "")))],
        "assembly_rows": [dict(row) for row in sorted(assemblies, key=lambda row: str(row.get("assembly_id", "")))],
        "nested_plant_rows": [dict(row) for row in sorted(nested_plants, key=lambda row: str(row.get("plant_system_id", "")))],
        "hazard_escalation_events": [dict(row) for row in hazard_events],
        "shard_partition_map": dict((key, str(shard_map[key])) for key in sorted(shard_map.keys())),
        "system_ids": list(sorted(all_system_ids)),
    }


def _roi_paths(*, seed: int, tick_horizon: int, system_ids: List[str], player_count: int, roi_width: int) -> List[dict]:
    rows: List[dict] = []
    if not system_ids:
        return rows
    horizon = int(max(1, _as_int(tick_horizon, 1)))
    players = int(max(1, _as_int(player_count, 2)))
    width = int(max(1, min(len(system_ids), _as_int(roi_width, 20))))
    for tick in range(horizon):
        for player_idx in range(players):
            start = _pick(seed, "roi.start", tick * 100 + player_idx, len(system_ids))
            roi_ids = [
                system_ids[(start + offset) % len(system_ids)]
                for offset in range(width)
            ]
            inspection_ids = [
                roi_ids[_pick(seed, "roi.inspect", tick * 100 + player_idx, len(roi_ids))]
            ]
            rows.append(
                {
                    "tick": int(tick),
                    "player_subject_id": "subject.player.{}".format(str(player_idx + 1).zfill(3)),
                    "roi_system_ids": list(sorted(set(roi_ids))),
                    "inspection_system_ids": list(sorted(set(inspection_ids))),
                }
            )
    return sorted(rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("player_subject_id", ""))))


def generate_sys_stress_scenario(
    *,
    seed: int,
    system_count: int,
    nested_size: int,
    tick_horizon: int,
    shard_count: int,
    player_count: int,
    roi_width: int,
    time_warp_batch_size: int,
) -> dict:
    seed_value = int(max(1, _as_int(seed, 1)))
    total_systems = int(max(1, _as_int(system_count, 512)))
    horizon = int(max(4, _as_int(tick_horizon, 64)))
    shard_total = int(max(1, _as_int(shard_count, 4)))
    nested_group = int(max(2, _as_int(nested_size, 20)))
    batch_size = int(max(1, _as_int(time_warp_batch_size, 4)))

    sys_payload = _system_rows(
        seed=seed_value,
        tick_horizon=horizon,
        system_count=total_systems,
        nested_size=nested_group,
        shard_count=shard_total,
    )
    system_ids = list(sys_payload.get("system_ids") or [])
    roi_rows = _roi_paths(
        seed=seed_value,
        tick_horizon=horizon,
        system_ids=system_ids,
        player_count=player_count,
        roi_width=roi_width,
    )

    expected_invariants_summary = {
        "must_preserve": [
            "INV-SYS-INVARIANTS-ALWAYS-CHECKED",
            "INV-NO-SILENT-TIER-TRANSITION",
            "INV-SYS-BUDGETED",
        ],
        "proof_chains": [
            "system_tier_change_hash_chain",
            "collapse_expand_event_hash_chain",
            "system_macro_output_record_hash_chain",
            "system_forced_expand_event_hash_chain",
            "system_health_hash_chain",
            "system_certification_result_hash_chain",
        ],
    }

    initial_state = {
        "schema_version": "1.0.0",
        "simulation_time": {
            "tick": 0,
            "tick_rate": 1,
            "deterministic_clock": {"tick_duration_ms": 1000},
        },
        "system_rows": [dict(row) for row in list(sys_payload.get("system_rows") or [])],
        "system_interface_signature_rows": [dict(row) for row in list(sys_payload.get("system_interface_signature_rows") or [])],
        "system_boundary_invariant_rows": [dict(row) for row in list(sys_payload.get("system_boundary_invariant_rows") or [])],
        "system_macro_capsule_rows": [dict(row) for row in list(sys_payload.get("system_macro_capsule_rows") or [])],
        "system_state_vector_rows": [dict(row) for row in list(sys_payload.get("system_state_vector_rows") or [])],
        "assembly_rows": [dict(row) for row in list(sys_payload.get("assembly_rows") or [])],
        "system_collapse_event_rows": [],
        "system_expand_event_rows": [],
        "system_tier_change_event_rows": [],
        "system_macro_output_record_rows": [],
        "system_macro_runtime_state_rows": [],
        "system_forced_expand_event_rows": [],
        "system_health_state_rows": [],
        "system_failure_event_rows": [],
        "system_reliability_warning_rows": [],
        "system_reliability_safe_fallback_rows": [],
        "system_reliability_output_adjustment_rows": [],
        "system_reliability_rng_outcome_rows": [],
        "system_certification_result_rows": [],
        "system_certificate_artifact_rows": [],
        "system_certificate_revocation_rows": [],
        "model_hazard_rows": [],
        "safety_events": [],
        "chem_degradation_event_rows": [],
        "control_decision_log": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
        "explain_artifact_rows": [],
        "compaction_markers": [],
        "system_tier_change_hash_chain": "",
        "collapse_expand_event_hash_chain": "",
        "system_macro_output_record_hash_chain": "",
        "system_forced_expand_event_hash_chain": "",
        "system_health_hash_chain": "",
        "system_certification_result_hash_chain": "",
    }

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.sys.stress.{}".format(
            canonical_sha256(
                {
                    "seed": int(seed_value),
                    "system_count": int(total_systems),
                    "tick_horizon": int(horizon),
                    "shard_count": int(shard_total),
                    "nested_size": int(nested_group),
                }
            )[:12]
        ),
        "scenario_seed": int(seed_value),
        "tick_horizon": int(horizon),
        "system_count": int(total_systems),
        "system_ids": list(system_ids),
        "nested_plant_rows": [dict(row) for row in list(sys_payload.get("nested_plant_rows") or [])],
        "mixed_domain_kinds": list(_SYSTEM_KINDS),
        "hazard_escalation_events": [dict(row) for row in list(sys_payload.get("hazard_escalation_events") or [])],
        "roi_movement_rows": [dict(row) for row in roi_rows],
        "time_warp_policy": {
            "policy_id": "temp.sys8.time_warp",
            "batch_size": int(batch_size),
            "substep_policy_id": "substep.fixed",
        },
        "shard_partition_map": dict(sys_payload.get("shard_partition_map") or {}),
        "shard_boundary_rules": {
            "cross_shard_expand_requires_boundary_request": True,
            "collapsed_cross_shard_requires_interface_exchange": True,
        },
        "expected_invariants_summary": dict(expected_invariants_summary),
        "budget_defaults": {
            "max_expands_per_tick": max(4, min(96, total_systems // 16)),
            "max_collapses_per_tick": max(8, min(128, total_systems // 8)),
            "max_macro_capsules_per_tick": max(16, min(256, total_systems // 4)),
            "max_health_updates_per_tick": max(16, min(256, total_systems // 4)),
            "max_reliability_evals_per_tick": max(16, min(256, total_systems // 4)),
            "macro_tick_bucket_stride": 1,
            "health_low_priority_stride": 2,
            "reliability_tick_bucket_stride": 1,
        },
        "initial_state_snapshot": initial_state,
        "deterministic_fingerprint": "",
        "extensions": {
            "generator": "tools/system/tool_generate_sys_stress.py",
            "named_rng_streams": [
                "rng.sys8.hazard_escalation",
                "rng.sys8.roi_path",
            ],
        },
    }
    scenario["deterministic_fingerprint"] = canonical_sha256(dict(scenario, deterministic_fingerprint=""))
    return scenario


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic SYS-8 stress scenario.")
    parser.add_argument("--seed", type=int, default=88017)
    parser.add_argument("--system-count", type=int, default=512)
    parser.add_argument("--nested-size", type=int, default=20)
    parser.add_argument("--tick-horizon", type=int, default=64)
    parser.add_argument("--shard-count", type=int, default=4)
    parser.add_argument("--player-count", type=int, default=2)
    parser.add_argument("--roi-width", type=int, default=18)
    parser.add_argument("--time-warp-batch-size", type=int, default=4)
    parser.add_argument("--output", default="build/system/sys8_stress_scenario.json")
    return parser


def main() -> int:
    args = _parser().parse_args()
    scenario = generate_sys_stress_scenario(
        seed=int(args.seed),
        system_count=int(args.system_count),
        nested_size=int(args.nested_size),
        tick_horizon=int(args.tick_horizon),
        shard_count=int(args.shard_count),
        player_count=int(args.player_count),
        roi_width=int(args.roi_width),
        time_warp_batch_size=int(args.time_warp_batch_size),
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, scenario)
    summary = {
        "output_path": output_abs,
        "scenario_id": str(scenario.get("scenario_id", "")),
        "system_count": int(_as_int(scenario.get("system_count", 0), 0)),
        "tick_horizon": int(_as_int(scenario.get("tick_horizon", 0), 0)),
        "deterministic_fingerprint": str(scenario.get("deterministic_fingerprint", "")),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

