#!/usr/bin/env python3
"""SIG-7 deterministic stress scenario generator."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _hash_roll(*, seed: int, stream: str, index: int, modulo: int) -> int:
    value = int(
        canonical_sha256(
            {
                "seed": int(seed),
                "stream": str(stream),
                "index": int(index),
            }
        )[:8],
        16,
    )
    return int(value % int(max(1, modulo)))


def _subject_ids(count: int) -> List[str]:
    return ["subject.sig.{:06d}".format(i) for i in range(int(max(1, count)))]


def _institution_ids(count: int) -> List[str]:
    return ["institution.sig.{:04d}".format(i) for i in range(int(max(1, count)))]


def _node_ids(count: int) -> List[str]:
    return ["node.sig.{:04d}".format(i) for i in range(int(max(2, count)))]


def _graph_rows(*, seed: int, topology: str, node_count: int) -> List[dict]:
    topo = str(topology or "ring").strip().lower() or "ring"
    nodes = _node_ids(node_count)
    edge_rows: List[dict] = []
    for idx in range(len(nodes)):
        from_node = nodes[idx]
        to_node = nodes[(idx + 1) % len(nodes)]
        edge_rows.append(
            {
                "edge_id": "edge.sig.{}".format(canonical_sha256({"f": from_node, "t": to_node})[:12]),
                "from_node_id": from_node,
                "to_node_id": to_node,
                "capacity": int(4 + _hash_roll(seed=seed, stream="edge.capacity", index=idx, modulo=12)),
                "delay_ticks": int(1 + _hash_roll(seed=seed, stream="edge.delay", index=idx, modulo=4)),
                "tags": ["tag.signal.attenuation.medium"],
            }
        )
    if topo == "hub":
        hub = nodes[0]
        for idx, node_id in enumerate(nodes[1:], start=1):
            edge_rows.append(
                {
                    "edge_id": "edge.sig.{}".format(canonical_sha256({"f": hub, "t": node_id, "k": "hub"})[:12]),
                    "from_node_id": hub,
                    "to_node_id": node_id,
                    "capacity": int(8 + _hash_roll(seed=seed, stream="hub.capacity", index=idx, modulo=16)),
                    "delay_ticks": int(1 + _hash_roll(seed=seed, stream="hub.delay", index=idx, modulo=3)),
                    "tags": ["tag.signal.attenuation.low"],
                }
            )
    elif topo == "mesh":
        for idx, from_node in enumerate(nodes):
            to_node = nodes[(idx + 3) % len(nodes)]
            if from_node == to_node:
                continue
            edge_rows.append(
                {
                    "edge_id": "edge.sig.{}".format(canonical_sha256({"f": from_node, "t": to_node, "k": "mesh"})[:12]),
                    "from_node_id": from_node,
                    "to_node_id": to_node,
                    "capacity": int(6 + _hash_roll(seed=seed, stream="mesh.capacity", index=idx, modulo=10)),
                    "delay_ticks": int(1 + _hash_roll(seed=seed, stream="mesh.delay", index=idx, modulo=3)),
                    "tags": ["tag.signal.attenuation.high"],
                }
            )
    return [
        {
            "schema_version": "1.0.0",
            "graph_id": "graph.sig.stress.{}".format(canonical_sha256({"seed": int(seed), "topology": topo})[:12]),
            "nodes": [{"node_id": node_id} for node_id in sorted(nodes)],
            "edges": sorted(
                (dict(row) for row in edge_rows),
                key=lambda row: str(row.get("edge_id", "")),
            ),
            "deterministic_routing_policy_id": "route.shortest_delay",
            "extensions": {"topology_kind": topo},
        }
    ]


def generate_sig_stress_scenario(
    *,
    seed: int,
    institution_count: int,
    subject_count: int,
    topology: str,
    tick_horizon: int,
) -> dict:
    seed_i = int(max(1, _as_int(seed, 1)))
    institutions = _institution_ids(int(max(1, institution_count)))
    subjects = _subject_ids(int(max(8, subject_count)))
    graph_rows = _graph_rows(
        seed=seed_i,
        topology=str(topology),
        node_count=max(8, min(512, int(len(subjects) // 16))),
    )
    graph_id = str(dict(graph_rows[0]).get("graph_id", "")).strip()
    node_rows = list(dict(graph_rows[0]).get("nodes") or [])
    node_ids = sorted(str(dict(row).get("node_id", "")).strip() for row in node_rows if str(dict(row).get("node_id", "")).strip())

    channel_rows = [
        {
            "schema_version": "1.0.0",
            "channel_id": "channel.sig.wired.stress",
            "channel_type_id": "channel.wired_basic",
            "network_graph_id": graph_id,
            "capacity_per_tick": 96,
            "base_delay_ticks": 1,
            "loss_policy_id": "loss.linear_attenuation",
            "encryption_policy_id": "enc.none",
            "deterministic_fingerprint": "",
            "extensions": {"routing_policy_id": "route.shortest_delay"},
        },
        {
            "schema_version": "1.0.0",
            "channel_id": "channel.sig.radio.stress",
            "channel_type_id": "channel.radio_basic",
            "network_graph_id": graph_id,
            "capacity_per_tick": 72,
            "base_delay_ticks": 1,
            "loss_policy_id": "loss.deterministic_rng",
            "encryption_policy_id": "enc.none",
            "deterministic_fingerprint": "",
            "extensions": {"routing_policy_id": "route.shortest_delay"},
        },
        {
            "schema_version": "1.0.0",
            "channel_id": "channel.local_institutional",
            "channel_type_id": "channel.local_institutional",
            "network_graph_id": graph_id,
            "capacity_per_tick": 128,
            "base_delay_ticks": 0,
            "loss_policy_id": "loss.none",
            "encryption_policy_id": "enc.none",
            "deterministic_fingerprint": "",
            "extensions": {"routing_policy_id": "route.shortest_delay"},
        },
    ]
    for row in channel_rows:
        seed_row = dict(row)
        seed_row["deterministic_fingerprint"] = ""
        row["deterministic_fingerprint"] = canonical_sha256(seed_row)

    institution_profiles: List[dict] = []
    group_membership_rows: List[dict] = []
    bulletin_schedule_rows: List[dict] = []
    bulletin_emit_rows: List[dict] = []
    dispatch_update_rows: List[dict] = []
    standards_issue_rows: List[dict] = []
    jamming_effect_rows: List[dict] = []
    key_rotation_rows: List[dict] = []

    for idx, institution_id in enumerate(institutions):
        node_id = node_ids[idx % len(node_ids)]
        group_id = "group.sig.inst.{:04d}".format(idx)
        subject_slice_start = (idx * max(1, len(subjects) // max(1, len(institutions)))) % len(subjects)
        member_count = max(8, len(subjects) // max(1, len(institutions)))
        members = sorted(
            subjects[(subject_slice_start + off) % len(subjects)]
            for off in range(member_count)
        )
        group_membership_rows.append(
            {
                "group_id": group_id,
                "subject_ids": members,
            }
        )
        policy_id = "bulletin.policy.sig.{:04d}".format(idx)
        schedule_id = "schedule.sig.bulletin.{:04d}".format(idx)
        cadence = int(4 + _hash_roll(seed=seed_i, stream="bulletin.cadence", index=idx, modulo=12))
        first_tick = int(_hash_roll(seed=seed_i, stream="bulletin.first", index=idx, modulo=max(2, cadence)))
        institution_profiles.append(
            {
                "schema_version": "1.0.0",
                "institution_id": institution_id,
                "bulletin_policy_id": policy_id,
                "dispatch_policy_id": "dispatch.rail_basic",
                "standards_policy_id": "standards.basic_body",
                "channels_available": ["channel.local_institutional", "channel.sig.wired.stress"],
                "deterministic_fingerprint": "",
                "extensions": {"home_node_id": node_id, "group_id": group_id},
            }
        )
        bulletin_schedule_rows.append(
            {
                "schedule_id": schedule_id,
                "next_due_tick": int(first_tick),
                "interval_ticks": int(cadence),
                "extensions": {"priority": "normal"},
            }
        )
        bulletin_emit_rows.append(
            {
                "institution_id": institution_id,
                "bulletin_policy_id": policy_id,
                "schedule_id": schedule_id,
                "channel_id": "channel.local_institutional",
                "group_id": group_id,
                "from_node_id": node_id,
                "priority": "normal",
            }
        )
        key_rotation_rows.append(
            {
                "institution_id": institution_id,
                "rotation_tick": int(8 + _hash_roll(seed=seed_i, stream="key.rotate", index=idx, modulo=max(16, tick_horizon))),
                "key_id_before": "key.group.{}.a".format(institution_id.replace(".", "_")),
                "key_id_after": "key.group.{}.b".format(institution_id.replace(".", "_")),
            }
        )
        dispatch_update_rows.append(
            {
                "schema_version": "1.0.0",
                "update_id": "dispatch.update.{}".format(canonical_sha256({"institution_id": institution_id, "i": idx})[:16]),
                "institution_id": institution_id,
                "schedule_id": "schedule.travel.{}".format(institution_id.replace(".", "_")),
                "vehicle_id": "vehicle.sig.{:04d}".format(idx),
                "itinerary_id": "itinerary.sig.{:04d}".format(idx),
                "schedule_kind": "travel.departure",
                "requested_tick": int(2 + _hash_roll(seed=seed_i, stream="dispatch.tick", index=idx, modulo=max(4, tick_horizon))),
                "priority": "passenger",
                "notes": "sig stress dispatch",
                "extensions": {},
            }
        )
        standards_issue_rows.append(
            {
                "schema_version": "1.0.0",
                "request_id": "request.spec.{}".format(canonical_sha256({"institution_id": institution_id, "i": idx})[:16]),
                "institution_id": institution_id,
                "spec_id": "spec.sig.standard.{:04d}".format(idx),
                "spec_type_id": "spec.track",
                "spec_parameters": {"limit": int(1 + _hash_roll(seed=seed_i, stream="spec.limit", index=idx, modulo=8))},
                "compliance_check_ids": ["check.sig.basic"],
                "notes": "stress-issued standard",
                "extensions": {},
            }
        )

    for idx in range(max(1, len(institutions) // 2)):
        channel_id = "channel.sig.radio.stress" if idx % 2 == 0 else "channel.sig.wired.stress"
        start_tick = int(3 + _hash_roll(seed=seed_i, stream="jam.start", index=idx, modulo=max(5, tick_horizon)))
        duration = int(2 + _hash_roll(seed=seed_i, stream="jam.duration", index=idx, modulo=7))
        jamming_effect_rows.append(
            {
                "schema_version": "1.0.0",
                "effect_id": "effect.jam.{}".format(canonical_sha256({"i": idx, "seed": seed_i})[:16]),
                "target_channel_id": channel_id,
                "strength_modifier": int(100 + _hash_roll(seed=seed_i, stream="jam.strength", index=idx, modulo=500)),
                "duration_ticks": int(duration),
                "start_tick": int(start_tick),
                "end_tick": int(start_tick + duration),
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        )

    for row in institution_profiles + jamming_effect_rows:
        seed_row = dict(row)
        seed_row["deterministic_fingerprint"] = ""
        row["deterministic_fingerprint"] = canonical_sha256(seed_row)

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.sig.stress.{}".format(canonical_sha256({"seed": seed_i})[:12]),
        "seed": int(seed_i),
        "tick_horizon": int(max(8, tick_horizon)),
        "topology": str(topology).strip().lower() or "ring",
        "institution_profile_rows": sorted(institution_profiles, key=lambda row: str(row.get("institution_id", ""))),
        "subject_ids": sorted(subjects),
        "network_graph_rows": graph_rows,
        "signal_channel_rows": sorted(channel_rows, key=lambda row: str(row.get("channel_id", ""))),
        "group_membership_rows": sorted(group_membership_rows, key=lambda row: str(row.get("group_id", ""))),
        "bulletin_schedule_rows": sorted(bulletin_schedule_rows, key=lambda row: str(row.get("schedule_id", ""))),
        "bulletin_emit_rows": sorted(bulletin_emit_rows, key=lambda row: str(row.get("institution_id", ""))),
        "dispatch_update_rows": sorted(dispatch_update_rows, key=lambda row: str(row.get("update_id", ""))),
        "standards_issue_request_rows": sorted(standards_issue_rows, key=lambda row: str(row.get("request_id", ""))),
        "jamming_effect_rows": sorted(jamming_effect_rows, key=lambda row: str(row.get("effect_id", ""))),
        "key_rotation_rows": sorted(key_rotation_rows, key=lambda row: (int(_as_int(row.get("rotation_tick", 0), 0)), str(row.get("institution_id", "")))),
        "artifact_refs": [
            {
                "artifact_type_id": "run_meta.sig_stress_scenario",
                "artifact_ref_id": "run_meta.sig.stress.{}".format(canonical_sha256({"seed": seed_i, "kind": "run_meta"})[:12]),
            },
            {
                "artifact_type_id": "scenario.pack.sig_stress",
                "artifact_ref_id": "scenario.pack.sig.{}".format(canonical_sha256({"seed": seed_i, "kind": "pack"})[:12]),
            },
        ],
        "deterministic_fingerprint": "",
    }
    seed_row = dict(scenario)
    seed_row["deterministic_fingerprint"] = ""
    scenario["deterministic_fingerprint"] = canonical_sha256(seed_row)
    return scenario


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic SIG-7 stress scenarios.")
    parser.add_argument("--seed", type=int, default=7001)
    parser.add_argument("--institutions", type=int, default=24)
    parser.add_argument("--subjects", type=int, default=4096)
    parser.add_argument("--topology", default="ring", choices=("ring", "mesh", "hub"))
    parser.add_argument("--ticks", type=int, default=128)
    parser.add_argument("--output", default="build/signals/sig_stress_scenario.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    scenario = generate_sig_stress_scenario(
        seed=int(max(1, args.seed)),
        institution_count=int(max(1, args.institutions)),
        subject_count=int(max(8, args.subjects)),
        topology=str(args.topology),
        tick_horizon=int(max(8, args.ticks)),
    )
    output = str(args.output).strip()
    if output:
        out_abs = os.path.normpath(os.path.abspath(output))
        _write_json(out_abs, scenario)
        scenario["output_path"] = out_abs
    print(json.dumps(scenario, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

