"""STRICT test: THERM-4 fire proof hash surfaces are stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_proof_hash_stable"
TEST_TAGS = ["strict", "thermal", "proof", "determinism"]


def _seed_surface() -> dict:
    return {
        "thermal_network_hash": "1" * 64,
        "overheat_event_hash_chain": "2" * 64,
        "ambient_exchange_hash": "3" * 64,
        "fire_state_hash_chain": "4" * 64,
        "ignition_event_hash_chain": "5" * 64,
        "fire_spread_hash_chain": "6" * 64,
        "runaway_event_hash_chain": "7" * 64,
        "signal_network_hash": "8" * 64,
        "message_delivery_event_hash_chain": "9" * 64,
        "receipt_hash_chain": "a" * 64,
        "trust_update_hash_chain": "b" * 64,
        "jamming_event_hash_chain": "c" * 64,
        "mobility_event_hash": "d" * 64,
        "congestion_hash": "e" * 64,
        "signal_state_hash": "f" * 64,
        "derailment_hash": "0" * 64,
        "power_flow_hash": "1" * 64,
        "power_flow_hash_chain": "2" * 64,
        "fault_state_hash_chain": "3" * 64,
        "protection_state_hash_chain": "4" * 64,
        "degradation_event_hash_chain": "5" * 64,
        "trip_event_hash_chain": "6" * 64,
        "trip_explanation_hash_chain": "7" * 64,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.proof.control_proof_bundle import build_control_proof_bundle_from_markers

    markers = [
        {
            "control_decision_id": "decision.therm4.001",
            "control_decision_log_hash": "a" * 64,
            "control_fidelity_allocation_hash": "b" * 64,
            "control_abstraction_downgrade_hash": "c" * 64,
            "control_view_policy_changes_hash": "d" * 64,
            "control_meta_override_hash": "e" * 64,
        }
    ]
    surface = _seed_surface()
    first = build_control_proof_bundle_from_markers(
        tick_start=120,
        tick_end=123,
        decision_markers=copy.deepcopy(markers),
        mobility_proof_surface=copy.deepcopy(surface),
    )
    second = build_control_proof_bundle_from_markers(
        tick_start=120,
        tick_end=123,
        decision_markers=copy.deepcopy(markers),
        mobility_proof_surface=copy.deepcopy(surface),
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "proof bundle drifted across identical THERM-4 fire surfaces"}
    for key in (
        "fire_state_hash_chain",
        "ignition_event_hash_chain",
        "fire_spread_hash_chain",
        "runaway_event_hash_chain",
    ):
        if len(str(first.get(key, "")).strip()) != 64:
            return {"status": "fail", "message": "missing/invalid proof hash field '{}'".format(key)}
    return {"status": "pass", "message": "THERM-4 fire proof hashes are stable"}

