"""FAST test: MOB-10 portal breach creates deterministic leak hazard and incident traces."""

from __future__ import annotations

import copy
import os
import sys


TEST_ID = "test_breach_creates_leak_hazard"
TEST_TAGS = ["fast", "mobility", "interior", "hazard", "incident"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from mobility_interior_testlib import authority_context, law_profile, policy_context, seed_state
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = seed_state(include_vehicle=True, vehicle_position_x=100)
    law = law_profile(["process.portal_seal_breach"])
    auth = authority_context(["entitlement.tool.operating"], privilege_level="operator", visibility_level="diegetic")
    policy = policy_context()

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.mob10.portal.breach.001",
            "process_id": "process.portal_seal_breach",
            "inputs": {"portal_id": "portal.mob10.cabin_hatch", "breach_magnitude": 180},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "portal seal breach refused unexpectedly"}

    leak_rows = [
        dict(row)
        for row in list(state.get("interior_leak_hazards") or [])
        if isinstance(row, dict) and str(dict(row.get("extensions") or {}).get("portal_id", "")).strip() == "portal.mob10.cabin_hatch"
    ]
    if not leak_rows:
        return {"status": "fail", "message": "portal breach did not create interior leak hazard"}

    provenance_rows = [
        dict(row)
        for row in list(state.get("compartment_provenance_events") or [])
        if isinstance(row, dict) and str(row.get("event_type", "")).strip() == "interior_portal_transition"
    ]
    if not provenance_rows:
        return {"status": "fail", "message": "portal breach did not emit interior portal transition provenance"}
    breach_event = next(
        (
            dict(row)
            for row in provenance_rows
            if str(dict(row.get("extensions") or {}).get("portal_id", "")).strip() == "portal.mob10.cabin_hatch"
        ),
        {},
    )
    if not breach_event:
        return {"status": "fail", "message": "missing breach provenance row for target portal"}
    breach_codes = set(str(token).strip() for token in list(dict(breach_event.get("extensions") or {}).get("incident_reason_codes") or []))
    if "incident.breach" not in breach_codes:
        return {"status": "fail", "message": "breach provenance missing incident.breach reason code"}
    if "incident.flooding_started" not in breach_codes:
        return {"status": "fail", "message": "breach provenance missing incident.flooding_started reason code"}

    travel_reason_codes = set()
    for row in list(state.get("travel_events") or []):
        if not isinstance(row, dict):
            continue
        details = dict(row.get("details") or {})
        reason_code = str(details.get("reason_code", "")).strip()
        if reason_code:
            travel_reason_codes.add(reason_code)
    if "incident.breach" not in travel_reason_codes:
        return {"status": "fail", "message": "travel incident stream missing incident.breach event"}

    interior_incident_rows = [
        dict(row)
        for row in list(state.get("vehicle_events") or [])
        if isinstance(row, dict) and str(row.get("event_kind", "")).strip() == "vehicle_interior_incident"
    ]
    if not interior_incident_rows:
        return {"status": "fail", "message": "vehicle interior incident event not emitted"}
    return {"status": "pass", "message": "breach path creates leak hazard and incident logs deterministically"}

