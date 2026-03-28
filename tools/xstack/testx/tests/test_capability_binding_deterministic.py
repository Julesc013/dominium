"""STRICT test: capability binding normalization is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_capability_binding_deterministic"
TEST_TAGS = ["strict", "control", "capability", "determinism"]


def _binding_rows() -> list[dict]:
    return [
        {
            "entity_id": "assembly.vehicle.alpha",
            "capability_id": "capability.can_be_driven",
            "parameters": {"control_binding_id": "binding.driver.alpha", "max_occupants": 2},
            "created_tick": 8,
        },
        {
            "entity_id": "assembly.vehicle.alpha",
            "capability_id": "capability.has_ports",
            "parameters": {},
            "created_tick": 8,
        },
        {
            "entity_id": "assembly.machine.beta",
            "capability_id": "capability.has_ports",
            "parameters": {"port_count": 4},
            "created_tick": 9,
        },
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.capability import (
        capability_binding_rows,
        get_capability_params,
        has_capability,
        normalize_capability_binding_rows,
    )
    from tools.xstack.compatx.canonical_json import canonical_sha256

    baseline_rows = _binding_rows()
    first = normalize_capability_binding_rows(copy.deepcopy(baseline_rows))
    second = capability_binding_rows({"record": {"capability_bindings": list(reversed(copy.deepcopy(baseline_rows)))}})

    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "capability binding normalization drifted across equivalent row orderings"}

    if [str(row.get("entity_id", "")) for row in first] != sorted(str(row.get("entity_id", "")) for row in first):
        return {"status": "fail", "message": "capability bindings are not sorted deterministically by entity_id"}

    if not has_capability(
        entity_id="assembly.vehicle.alpha",
        capability_id="capability.can_be_driven",
        capability_bindings=first,
    ):
        return {"status": "fail", "message": "has_capability did not resolve known capability binding"}

    params = get_capability_params(
        entity_id="assembly.vehicle.alpha",
        capability_id="capability.can_be_driven",
        capability_bindings=first,
    )
    if str(params.get("control_binding_id", "")) != "binding.driver.alpha":
        return {"status": "fail", "message": "get_capability_params lost deterministic parameter payload"}

    return {"status": "pass", "message": "capability binding normalization is deterministic"}

