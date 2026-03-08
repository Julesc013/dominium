"""FAST test: GEO profile overrides are logged and invariant-breaking dimension changes are refused."""

from __future__ import annotations

import json
import os

from src.geo import resolve_geo_profile_set


TEST_ID = "test_profile_override_logged"
TEST_TAGS = ["fast", "geo", "profile", "determinism"]


def run(repo_root: str):
    profile_registry_path = os.path.join(repo_root, "data", "registries", "profile_registry.json")
    try:
        profile_registry_payload = json.load(open(profile_registry_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "profile registry missing or invalid"}

    result = resolve_geo_profile_set(
        universe_identity={
            "topology_profile_id": "geo.topology.r3_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "partition_profile_id": "geo.partition.grid_zd",
            "projection_profile_id": "geo.projection.perspective_3d",
        },
        owner_context={
            "universe_id": "universe.test.geo",
            "session_id": "session.test.geo",
            "session_spec": {
                "save_id": "session.test.geo",
                "profile_bindings": [
                    {
                        "binding_id": "binding.geo.session.override",
                        "scope": "session",
                        "target_id": "session.test.geo",
                        "profile_id": "geo.topology.r4_stub",
                        "tick_applied": 0,
                        "extensions": {},
                    }
                ],
            },
        },
        profile_registry_payload=profile_registry_payload,
        tick=0,
        owner_id="session.test.geo",
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "dimension-changing override should refuse"}
    if str(result.get("refusal_code", "")) != "refusal.geo.dimension_change":
        return {"status": "fail", "message": "unexpected refusal code"}
    if not list(result.get("exception_events") or []):
        return {"status": "fail", "message": "override refusal did not emit exception event"}
    return {"status": "pass", "message": "geo profile override logging/refusal valid"}
