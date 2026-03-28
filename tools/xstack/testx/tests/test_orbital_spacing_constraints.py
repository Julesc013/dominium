"""FAST test: MW-2 orbital priors preserve deterministic periapsis ordering."""

from __future__ import annotations

import sys


TEST_ID = "test_orbital_spacing_constraints"
TEST_TAGS = ["fast", "mw", "worldgen", "orbit", "determinism", "l2"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    result = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=worldgen_request_row(
            request_id="mw2.orbital_spacing.constraints",
            index_tuple=[800, 0, 0],
            refinement_level=2,
            reason="query",
        ),
        cache_enabled=False,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-2 orbital-spacing fixture did not complete"}

    by_system = {}
    for row in list(result.get("generated_planet_orbit_artifact_rows") or []):
        if not isinstance(row, dict):
            continue
        extensions = dict(row.get("extensions") or {})
        system_object_id = str(extensions.get("parent_system_object_id", "")).strip()
        if not system_object_id:
            continue
        by_system.setdefault(system_object_id, []).append(dict(row))

    if not by_system:
        return {"status": "fail", "message": "MW-2 generated no orbit artifacts"}

    for system_object_id, rows in sorted(by_system.items()):
        previous_apoapsis = 0
        previous_axis = 0
        ordered = sorted(rows, key=lambda item: int(dict(item.get("extensions") or {}).get("planet_index", 0)))
        for row in ordered:
            axis = int((dict(row.get("semi_major_axis") or {})).get("value", 0) or 0)
            eccentricity = int((dict(row.get("eccentricity") or {})).get("value", 0) or 0)
            periapsis = (axis * (1000 - eccentricity)) // 1000
            apoapsis = (axis * (1000 + eccentricity) + 999) // 1000
            if axis < previous_axis:
                return {
                    "status": "fail",
                    "message": "MW-2 orbit ladder regressed for system {}".format(system_object_id),
                }
            if previous_axis > 0 and periapsis <= previous_apoapsis:
                return {
                    "status": "fail",
                    "message": "MW-2 orbit spacing violated periapsis ordering for system {}".format(system_object_id),
                }
            previous_axis = axis
            previous_apoapsis = apoapsis
    return {"status": "pass", "message": "MW-2 orbit spacing preserves deterministic periapsis ordering"}
