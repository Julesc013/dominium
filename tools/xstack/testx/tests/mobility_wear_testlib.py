"""Shared MOB-9 wear/maintenance TestX fixtures."""

from __future__ import annotations

import copy


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    law = construction_law_profile(list(allowed_processes or []))
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    admin_processes = (
        "process.inspect_track",
        "process.service_track",
        "process.inspect_vehicle",
        "process.service_vehicle",
        "process.mob_failure",
        "process.mob_track_failure",
    )
    for process_id in admin_processes:
        if process_id in set(law.get("allowed_processes") or []):
            entitlements[process_id] = "entitlement.control.admin"
            privileges[process_id] = "operator"
    if "process.mobility_wear_tick" in set(law.get("allowed_processes") or []):
        entitlements["process.mobility_wear_tick"] = "session.boot"
        privileges["process.mobility_wear_tick"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect"],
        privilege_level="operator",
    )


def policy_context() -> dict:
    from tools.xstack.testx.tests.mobility_travel_testlib import policy_context as travel_policy_context

    return copy.deepcopy(travel_policy_context())


def seed_state() -> dict:
    from tools.xstack.testx.tests.mobility_travel_testlib import seed_state as travel_seed_state

    state = travel_seed_state()
    state.setdefault("mobility_wear_states", [])
    state.setdefault("mobility_wear_pending_updates", [])
    state.setdefault("mobility_maintenance_schedules", [])
    state.setdefault("mobility_maintenance_due_events", [])
    state.setdefault("mobility_wear_runtime_state", {})
    return state

