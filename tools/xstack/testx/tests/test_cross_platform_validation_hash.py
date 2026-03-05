"""FAST test: SYS-1 validation fingerprints remain stable for equivalent payloads."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_cross_platform_validation_hash"
TEST_TAGS = ["fast", "system", "sys1", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from src.system import validate_boundary_invariants, validate_interface_signature
    from tools.xstack.testx.tests.sys1_testlib import cloned_state, validation_payloads

    base_state = cloned_state()
    reordered_state = copy.deepcopy(base_state)
    interface_rows = list(reordered_state.get("system_interface_signature_rows") or [])
    if interface_rows:
        interface_rows[0]["port_list"] = list(reversed(list(interface_rows[0].get("port_list") or [])))
        interface_rows[0]["signal_descriptors"] = list(
            reversed(list(interface_rows[0].get("signal_descriptors") or []))
        )
    reordered_state["system_boundary_invariant_rows"] = list(
        reversed(list(reordered_state.get("system_boundary_invariant_rows") or []))
    )

    registries = validation_payloads(repo_root=repo_root)

    base_interface = validate_interface_signature(
        system_id="system.engine.alpha",
        system_rows=base_state.get("system_rows") or [],
        interface_signature_rows=base_state.get("system_interface_signature_rows") or [],
        quantity_bundle_registry_payload=registries.get("quantity_bundle_registry_payload"),
        spec_type_registry_payload=registries.get("spec_type_registry_payload"),
        signal_channel_type_registry_payload=registries.get("signal_channel_type_registry_payload"),
    )
    base_invariants = validate_boundary_invariants(
        system_id="system.engine.alpha",
        system_rows=base_state.get("system_rows") or [],
        boundary_invariant_rows=base_state.get("system_boundary_invariant_rows") or [],
        boundary_invariant_template_registry_payload=registries.get("boundary_invariant_template_registry_payload"),
        tolerance_policy_registry_payload=registries.get("tolerance_policy_registry_payload"),
        safety_pattern_registry_payload=registries.get("safety_pattern_registry_payload"),
    )

    reordered_interface = validate_interface_signature(
        system_id="system.engine.alpha",
        system_rows=reordered_state.get("system_rows") or [],
        interface_signature_rows=reordered_state.get("system_interface_signature_rows") or [],
        quantity_bundle_registry_payload=registries.get("quantity_bundle_registry_payload"),
        spec_type_registry_payload=registries.get("spec_type_registry_payload"),
        signal_channel_type_registry_payload=registries.get("signal_channel_type_registry_payload"),
    )
    reordered_invariants = validate_boundary_invariants(
        system_id="system.engine.alpha",
        system_rows=reordered_state.get("system_rows") or [],
        boundary_invariant_rows=reordered_state.get("system_boundary_invariant_rows") or [],
        boundary_invariant_template_registry_payload=registries.get("boundary_invariant_template_registry_payload"),
        tolerance_policy_registry_payload=registries.get("tolerance_policy_registry_payload"),
        safety_pattern_registry_payload=registries.get("safety_pattern_registry_payload"),
    )

    fingerprint_a = canonical_sha256(
        {
            "interface": str(base_interface.get("deterministic_fingerprint", "")).strip(),
            "invariants": str(base_invariants.get("deterministic_fingerprint", "")).strip(),
        }
    )
    fingerprint_b = canonical_sha256(
        {
            "interface": str(reordered_interface.get("deterministic_fingerprint", "")).strip(),
            "invariants": str(reordered_invariants.get("deterministic_fingerprint", "")).strip(),
        }
    )
    if not fingerprint_a or not fingerprint_b:
        return {"status": "fail", "message": "validation fingerprints were not produced"}
    if fingerprint_a != fingerprint_b:
        return {"status": "fail", "message": "validation fingerprint changed for equivalent reordered payload"}
    return {"status": "pass", "message": "validation fingerprints stable across equivalent payload ordering"}
