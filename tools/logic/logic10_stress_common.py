"""Shared deterministic scenario builders for LOGIC-10 stress/proof tooling."""

from __future__ import annotations

import json
import os
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.logic.tool_run_logic_debug_stress import build_logic_debug_stress_scenario
from tools.logic.tool_run_logic_eval_stress import build_logic_eval_stress_scenario
from tools.logic.tool_run_logic_timing_stress import build_logic_timing_stress_scenario
from tools.xstack.testx.tests._logic_eval_test_utils import make_loop_network


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _token(value: object) -> str:
    return str(value or "").strip()


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _pick(seed: int, stream: str, index: int, modulo: int, *, offset: int = 0) -> int:
    mod = int(max(1, _as_int(modulo, 1)))
    digest = canonical_sha256(
        {
            "seed": int(seed),
            "stream": str(stream),
            "index": int(index),
            "modulo": int(mod),
        }
    )
    return int(int(offset) + (int(digest[:12], 16) % mod))


def build_logic_mega_network_descriptor(
    *,
    seed: int,
    mega_node_count: int = 1_000_000,
    shard_count: int = 16,
    controller_count: int = 4096,
) -> dict:
    node_count = int(max(1, _as_int(mega_node_count, 1_000_000)))
    shard_total = int(max(1, _as_int(shard_count, 16)))
    controller_total = int(max(1, _as_int(controller_count, 4096)))
    edge_count = int(node_count + (node_count // 2))
    sequential_controller_count = int(max(1, controller_total // 3))
    combinational_controller_count = int(max(1, controller_total - sequential_controller_count))
    state_space_bound = int(sequential_controller_count * 32)
    bus_count = int(max(1, controller_total // 4))
    descriptor = {
        "scenario_id": "scenario.logic10.mega.{}".format(
            canonical_sha256(
                {
                    "seed": int(seed),
                    "mega_node_count": node_count,
                    "shard_count": shard_total,
                    "controller_count": controller_total,
                }
            )[:12]
        ),
        "network_id": "net.logic.mega.compiled",
        "description": "Deterministic mega-network descriptor for compile-eligibility and regression anchoring.",
        "node_count": int(node_count),
        "edge_count": int(edge_count),
        "controller_count": int(controller_total),
        "combinational_controller_count": int(combinational_controller_count),
        "sequential_controller_count": int(sequential_controller_count),
        "bus_count": int(bus_count),
        "shard_count": int(shard_total),
        "state_space_bound_nodes": int(state_space_bound),
        "carrier_mix": ["carrier.electrical", "carrier.mechanical", "carrier.optical", "carrier.sig"],
        "compile_targets": {
            "compiled.reduced_graph": True,
            "compiled.automaton": bool(state_space_bound <= 262144),
            "compiled.lookup_table": False,
        },
        "compile_eligibility": {
            "validated_graph_required": True,
            "state_vectors_declared": True,
            "timing_constraints_bounded": True,
            "forbidden_loops_present": False,
            "protocol_links_boundary_safe": True,
        },
        "proof_requirements": {
            "equivalence_required": True,
            "allow_bounded_error": False,
            "compiled_only_loops_forbidden_without_proof": True,
        },
        "deterministic_source_hash": canonical_sha256(
            {
                "seed": int(seed),
                "node_count": node_count,
                "edge_count": edge_count,
                "controller_count": controller_total,
                "shard_count": shard_total,
                "state_space_bound_nodes": state_space_bound,
            }
        ),
    }
    descriptor["compile_eligibility_hash"] = canonical_sha256(
        {
            "compile_targets": descriptor["compile_targets"],
            "compile_eligibility": descriptor["compile_eligibility"],
            "proof_requirements": descriptor["proof_requirements"],
        }
    )
    descriptor["deterministic_fingerprint"] = canonical_sha256(dict(descriptor, deterministic_fingerprint=""))
    return descriptor


def _build_loop_refusal_payload(*, network_id: str) -> dict:
    _binding, logic_network_state = make_loop_network(network_id=network_id)
    return {
        "scenario_id": "scenario.logic10.loop.{}".format(canonical_sha256({"network_id": network_id})[:12]),
        "logic_network_state": logic_network_state,
        "signal_store_state": {},
        "logic_eval_state": {},
        "state_vector_snapshot_rows": [],
        "evaluation_requests": [{"tick": 1, "network_id": network_id}],
        "deterministic_fingerprint": canonical_sha256({"network_id": network_id, "kind": "loop_refusal"}),
    }


def generate_logic_stress_scenario(
    *,
    repo_root: str,
    seed: int = 1010,
    tick_count: int = 8,
    network_count: int = 12,
    mega_node_count: int = 1_000_000,
) -> dict:
    base_seed = int(max(1, _as_int(seed, 1010)))
    total_ticks = int(max(4, _as_int(tick_count, 8)))
    scale_network_count = int(max(4, _as_int(network_count, 12)))

    eval_pairs = int(max(8, 16 + _pick(base_seed, "logic10.eval_pairs", 0, 24)))
    timing_oscillators = int(max(4, 6 + _pick(base_seed, "logic10.timing_oscillators", 1, 12)))
    debug_sessions = int(max(8, 10 + _pick(base_seed, "logic10.debug_sessions", 2, 18)))
    protocol_frames = int(max(8, 12 + _pick(base_seed, "logic10.protocol_frames", 3, 16)))
    fault_ticks = int(max(4, total_ticks))

    eval_payload = build_logic_eval_stress_scenario(
        repo_root=repo_root,
        element_pairs=eval_pairs,
        tick_count=total_ticks,
    )
    timing_payload = build_logic_timing_stress_scenario(
        repo_root=repo_root,
        oscillator_count=timing_oscillators,
        tick_count=total_ticks,
    )
    debug_payload = build_logic_debug_stress_scenario(
        repo_root=repo_root,
        session_count=debug_sessions,
        tick_count=total_ticks,
    )
    loop_payload = _build_loop_refusal_payload(network_id="net.logic10.loop.refusal")
    mega_descriptor = build_logic_mega_network_descriptor(
        seed=base_seed,
        mega_node_count=mega_node_count,
        shard_count=max(4, scale_network_count // 2),
        controller_count=max(512, scale_network_count * 256),
    )

    distributed_descriptor = {
        "scenario_id": "scenario.logic10.distributed.{}".format(
            canonical_sha256({"seed": base_seed, "kind": "distributed"})[:12]
        ),
        "controller_count": int(max(64, scale_network_count * 96)),
        "region_count": int(max(4, scale_network_count // 2)),
        "shard_count": int(max(4, scale_network_count // 2)),
        "carrier_type_id": "carrier.sig",
        "boundary_artifact_count": int(max(8, scale_network_count * 6)),
        "protocol_link_count": int(max(16, scale_network_count * 10)),
        "remote_monitoring_enabled": True,
        "debug_force_expand_budgeted": True,
        "security_policy_id": "sec.auth_required_stub",
        "deterministic_fingerprint": canonical_sha256(
            {
                "seed": base_seed,
                "controller_count": int(max(64, scale_network_count * 96)),
                "region_count": int(max(4, scale_network_count // 2)),
                "protocol_link_count": int(max(16, scale_network_count * 10)),
            }
        ),
    }

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.logic10.envelope.{}".format(
            canonical_sha256(
                {
                    "seed": base_seed,
                    "tick_count": total_ticks,
                    "network_count": scale_network_count,
                    "mega_node_count": int(max(1, _as_int(mega_node_count, 1_000_000))),
                }
            )[:12]
        ),
        "seed": int(base_seed),
        "tick_count": int(total_ticks),
        "network_count": int(scale_network_count),
        "generator": "tools/logic/tool_generate_logic_stress.py",
        "scale_networks": {
            "eval_uncompiled_payload": eval_payload,
            "timing_oscillation_payload": timing_payload,
            "debug_load_payload": debug_payload,
        },
        "distributed_control": distributed_descriptor,
        "adversarial_patterns": {
            "loop_refusal_payload": loop_payload,
            "oscillation_payload": timing_payload,
            "timing_violation_expected": True,
            "compute_overload_expected": True,
        },
        "protocol_contention": {
            "frame_count": int(protocol_frames),
            "tick_count": int(total_ticks),
            "use_sig": True,
            "arbitration_policy_ids": ["arb.fixed_priority", "arb.time_slice", "arb.token"],
            "security_policy_id": "sec.auth_required_stub",
        },
        "fault_security": {
            "tick_count": int(fault_ticks),
            "fault_kind_ids": ["fault.open", "fault.short", "fault.stuck_at_0", "fault.stuck_at_1"],
            "security_block_expected": True,
            "named_rng_noise_policy_id": "noise.named_rng_optional",
        },
        "debug_load": {
            "session_count": int(debug_sessions),
            "sampling_policy_id": "debug.sample.lab_high",
            "throttle_expected": True,
            "forced_expand_expected": True,
        },
        "mega_network": mega_descriptor,
        "expected_invariant_summary": {
            "determinism_across_thread_counts": True,
            "no_unbounded_loops": True,
            "compute_budget_respected": True,
            "coupling_budget_respected": True,
            "compiled_preference_under_pressure": True,
            "security_blocks_deterministic": True,
            "loop_refusal_deterministic": True,
            "trace_compaction_stable": True,
            "proof_chain_complete": True,
        },
    }
    scenario["deterministic_fingerprint"] = canonical_sha256(dict(scenario, deterministic_fingerprint=""))
    return scenario


__all__ = [
    "_as_int",
    "_pick",
    "_token",
    "_write_json",
    "build_logic_mega_network_descriptor",
    "generate_logic_stress_scenario",
]
