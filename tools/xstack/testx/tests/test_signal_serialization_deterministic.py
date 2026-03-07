"""FAST test: LOGIC-1 signal serialization and hashing are deterministic."""

from __future__ import annotations


TEST_ID = "test_signal_serialization_deterministic"
TEST_TAGS = ["fast", "logic", "signal", "determinism"]


def run(repo_root: str):
    del repo_root
    from src.logic.signal import canonical_signal_hash, canonical_signal_serialization

    row_a = {
        "signal_id": "signal.logic.a",
        "signal_type_id": "signal.boolean",
        "carrier_type_id": "carrier.electrical",
        "value_ref": {"value_kind": "boolean", "value": 1},
        "valid_from_tick": 4,
        "valid_until_tick": None,
        "extensions": {
            "slot": {"network_id": "net.logic", "element_id": "elem.a", "port_id": "port.out"},
            "delay_policy_id": "delay.none",
            "noise_policy_id": "noise.none",
        },
    }
    row_b = {
        "signal_id": "signal.logic.b",
        "signal_type_id": "signal.scalar",
        "carrier_type_id": "carrier.electrical",
        "value_ref": {"value_kind": "scalar", "value_fixed": 25},
        "valid_from_tick": 4,
        "valid_until_tick": None,
        "extensions": {
            "slot": {"network_id": "net.logic", "element_id": "elem.b", "port_id": "port.out"},
            "delay_policy_id": "delay.none",
            "noise_policy_id": "noise.none",
        },
    }
    state_a = {"signal_rows": [row_a, row_b]}
    state_b = {"signal_rows": [row_b, row_a]}
    serialization_a = canonical_signal_serialization(state=state_a, tick=4)
    serialization_b = canonical_signal_serialization(state=state_b, tick=4)
    hash_a = canonical_signal_hash(state=state_a, tick=4)
    hash_b = canonical_signal_hash(state=state_b, tick=4)
    if serialization_a != serialization_b or hash_a != hash_b:
        return {"status": "fail", "message": "signal serialization/hash must be order invariant"}
    return {"status": "pass", "message": "signal serialization/hash deterministic"}
