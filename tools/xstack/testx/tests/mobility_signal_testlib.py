"""Shared MOB-8 signaling/interlocking TestX fixtures."""

from __future__ import annotations

import copy


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    law = construction_law_profile(list(allowed_processes or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    admin_processes = (
        "process.signal_set_aspect",
        "process.switch_set_state",
        "process.switch_lock",
        "process.switch_unlock",
        "process.route_reserve_blocks",
        "process.signal_hazard_set",
    )
    observer_processes = (
        "process.signal_tick",
        "process.signal_maintenance_tick",
        "process.mobility_micro_tick",
    )
    for process_id in admin_processes:
        if process_id in set(law.get("allowed_processes") or []):
            entitlements[process_id] = "entitlement.control.admin"
            privileges[process_id] = "operator"
    for process_id in observer_processes:
        if process_id in set(law.get("allowed_processes") or []):
            entitlements[process_id] = "session.boot"
            privileges[process_id] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["entitlement.control.admin", "session.boot", "entitlement.inspect"],
        privilege_level="operator",
    )


def policy_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    policy = copy.deepcopy(construction_policy_context(max_compute_units_per_tick=4096))
    policy["signal_type_registry"] = {
        "record": {
            "signal_types": [
                {
                    "schema_version": "1.0.0",
                    "signal_type_id": "signal.rail_block_basic",
                    "schema_ref": "dominium.schema.mobility.signal@1.0.0",
                    "extensions": {},
                }
            ]
        }
    }
    policy["signal_rule_policy_registry"] = {
        "record": {
            "signal_rule_policies": [
                {
                    "schema_version": "1.0.0",
                    "rule_policy_id": "policy.rail_basic_interlocking",
                    "schema_ref": "dominium.schema.mobility.signal_rule_policy@1.0.0",
                    "extensions": {
                        "description": "basic interlocking",
                        "aspects": ["stop", "caution", "clear"],
                        "transition_rules": [],
                        "interlocking_rules": [],
                    },
                },
                {
                    "schema_version": "1.0.0",
                    "rule_policy_id": "policy.rail_strict_interlocking",
                    "schema_ref": "dominium.schema.mobility.signal_rule_policy@1.0.0",
                    "extensions": {
                        "description": "strict interlocking",
                        "aspects": ["stop", "caution", "clear"],
                        "transition_rules": [],
                        "interlocking_rules": [{"rule_id": "rule.strict", "requires_unreserved": True}],
                    },
                },
            ]
        }
    }
    return policy


def seed_signal_state(*, signal_count: int = 1, initial_aspect: str = "clear", initial_velocity: int = 0) -> dict:
    from src.mobility.signals import build_signal_state_machine
    from tools.xstack.testx.tests.mobility_micro_testlib import seed_micro_state

    state = seed_micro_state(initial_velocity=int(initial_velocity))
    signal_rows = []
    machine_rows = []
    count = int(max(1, int(signal_count)))
    for idx in range(count):
        suffix = str(idx + 1).zfill(2)
        signal_id = "signal.mob.test.{}".format(suffix)
        machine_id = "state_machine.mob.signal.{}".format(suffix)
        signal_rows.append(
            {
                "schema_version": "1.0.0",
                "signal_id": signal_id,
                "attached_to": {"edge_id": "edge.mob.micro.main"},
                "signal_type_id": "signal.rail_block_basic",
                "state_machine_id": machine_id,
                "rule_policy_id": "policy.rail_basic_interlocking",
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        )
        machine_rows.append(
            build_signal_state_machine(
                signal_id=signal_id,
                state_machine_id=machine_id,
                aspects=["stop", "caution", "clear"],
                initial_aspect=str(initial_aspect).strip().lower() or "clear",
            )
        )
    state["mobility_signals"] = signal_rows
    state["mobility_signal_state_machines"] = machine_rows
    state.setdefault("mobility_block_reservations", [])
    state.setdefault("mobility_switch_locks", [])
    state.setdefault("mobility_signal_hazards", [])
    return state
