"""Shared SAFETY-0 TestX fixtures."""

from __future__ import annotations

import copy


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    return construction_law_profile(list(allowed_processes or []))


def authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect"],
        privilege_level="operator",
    )


def policy_context(*, max_compute_units_per_tick: int = 4096) -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    return copy.deepcopy(
        construction_policy_context(
            max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick))),
        )
    )


def base_state(*, current_tick: int = 0) -> dict:
    from tools.xstack.testx.tests.construction_testlib import base_state as construction_base_state

    state = copy.deepcopy(construction_base_state())
    state["simulation_time"] = {
        "tick": int(max(0, int(current_tick))),
        "tick_rate": 1,
        "deterministic_clock": {"tick_duration_ms": 1000},
    }
    state.setdefault("mobility_switch_state_machines", [])
    state.setdefault("mobility_switch_locks", [])
    state.setdefault("mobility_signals", [])
    state.setdefault("mobility_signal_state_machines", [])
    state.setdefault("signal_channel_rows", [])
    state.setdefault("signal_channels", [])
    state.setdefault("safety_instances", [])
    state.setdefault("safety_events", [])
    state.setdefault(
        "safety_runtime_state",
        {
            "schema_version": "1.0.0",
            "last_tick": 0,
            "last_budget_outcome": "complete",
            "last_processed_instance_count": 0,
            "last_deferred_instance_count": 0,
            "last_triggered_instance_count": 0,
            "last_event_count": 0,
            "heartbeat_rows": [],
            "extensions": {},
        },
    )
    return state


def seed_signal_state(
    state: dict,
    *,
    signal_id: str = "signal.safety.test",
    machine_id: str = "state_machine.safety.signal",
    initial_aspect: str = "clear",
) -> dict:
    from mobility.signals import build_signal_state_machine

    out = copy.deepcopy(state)
    out["mobility_signals"] = [
        {
            "schema_version": "1.0.0",
            "signal_id": str(signal_id),
            "attached_to": {"edge_id": "edge.safety.main"},
            "signal_type_id": "signal.rail_block_basic",
            "state_machine_id": str(machine_id),
            "rule_policy_id": "policy.rail_basic_interlocking",
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    out["mobility_signal_state_machines"] = [
        build_signal_state_machine(
            signal_id=str(signal_id),
            state_machine_id=str(machine_id),
            aspects=["stop", "caution", "clear"],
            initial_aspect=str(initial_aspect).strip().lower() or "clear",
        )
    ]
    out.setdefault("edge_occupancies", [])
    return out


def seed_switch_state(
    state: dict,
    *,
    machine_id: str = "machine.safety.switch",
    state_id: str = "edge.safety.main",
) -> dict:
    out = copy.deepcopy(state)
    out["mobility_switch_state_machines"] = [
        {
            "schema_version": "1.0.0",
            "machine_id": str(machine_id),
            "machine_type_id": "state_machine.mobility.switch",
            "state_id": str(state_id),
            "transitions": [],
            "transition_rows": [],
            "extensions": {},
        }
    ]
    out.setdefault("network_graphs", [])
    return out
