"""FAST test: INT-3 interior overlay ordering is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.interior.overlay_ordering_deterministic"
TEST_TAGS = ["fast", "interior", "render", "determinism"]


def _inspection_snapshot() -> dict:
    return {
        "target_payload": {
            "target_id": "interior.graph.test.alpha",
            "exists": True,
            "collection": "interior_graphs",
            "row": {
                "schema_version": "1.0.0",
                "graph_id": "interior.graph.test.alpha",
                "volumes": ["volume.a", "volume.b"],
                "portals": ["portal.ab"],
                "extensions": {},
            },
        },
        "summary_sections": {
            "section.interior.connectivity_summary": {
                "data": {
                    "available": True,
                    "graph_id": "interior.graph.test.alpha",
                    "volume_count": 2,
                    "portal_count": 1,
                    "open_portal_count": 0,
                    "blocked_portal_count": 1,
                }
            },
            "section.interior.portal_state_table": {
                "data": {
                    "available": True,
                    "graph_id": "interior.graph.test.alpha",
                    "portal_states": [
                        {
                            "portal_id": "portal.ab",
                            "portal_type_id": "portal.door",
                            "from_volume_id": "volume.a",
                            "to_volume_id": "volume.b",
                            "state_machine_id": "state.portal.ab",
                            "state_id": "closed",
                            "sealing_coefficient": 900,
                        }
                    ],
                }
            },
            "section.interior.pressure_summary": {
                "data": {
                    "available": True,
                    "rows": [
                        {"volume_id": "volume.a", "derived_pressure": 1100, "oxygen_fraction": 205},
                        {"volume_id": "volume.b", "derived_pressure": 900, "oxygen_fraction": 210},
                    ]
                }
            },
            "section.interior.flood_summary": {
                "data": {
                    "available": True,
                    "rows": [
                        {"volume_id": "volume.a", "water_volume": 300, "smoke_density": 260},
                        {"volume_id": "volume.b", "water_volume": 0, "smoke_density": 0},
                    ],
                    "flooded_count": 1,
                }
            },
            "section.interior.smoke_summary": {
                "data": {
                    "available": True,
                    "rows": [
                        {"volume_id": "volume.a", "smoke_density": 260},
                        {"volume_id": "volume.b", "smoke_density": 0},
                    ],
                    "warn_count": 1,
                    "danger_count": 0,
                }
            },
            "section.interior.flow_summary": {
                "data": {
                    "available": True,
                    "leaks": [
                        {
                            "leak_id": "leak.a",
                            "volume_id": "volume.a",
                            "leak_rate_air": 10,
                            "leak_rate_water": 1,
                            "hazard_model_id": "hazard.leak.a",
                        }
                    ],
                    "portal_flow_rows": [
                        {
                            "portal_id": "portal.ab",
                            "portal_type_id": "portal.door",
                            "sealing_coefficient": 900,
                            "conductance_air": 300,
                            "conductance_water": 100,
                            "conductance_smoke": 150,
                        }
                    ],
                }
            },
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.interaction.inspection_overlays import build_inspection_overlays
    from tools.xstack.compatx.canonical_json import canonical_sha256

    snapshot = _inspection_snapshot()
    perceived = {"time_state": {"tick": 10}, "entities": {"entries": []}, "populations": {"entries": []}}

    first = build_inspection_overlays(
        perceived_model=copy.deepcopy(perceived),
        target_semantic_id="interior.graph.test.alpha",
        authority_context={},
        inspection_snapshot=copy.deepcopy(snapshot),
        overlay_runtime={"repo_root": str(repo_root)},
        requested_cost_units=1,
    )
    second = build_inspection_overlays(
        perceived_model=copy.deepcopy(perceived),
        target_semantic_id="interior.graph.test.alpha",
        authority_context={},
        inspection_snapshot=copy.deepcopy(snapshot),
        overlay_runtime={"repo_root": str(repo_root)},
        requested_cost_units=1,
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "interior overlay build did not complete deterministically"}

    first_payload = dict(first.get("inspection_overlays") or {})
    second_payload = dict(second.get("inspection_overlays") or {})
    if canonical_sha256(first_payload) != canonical_sha256(second_payload):
        return {"status": "fail", "message": "interior overlay payload hash mismatch across identical inputs"}

    renderables = [dict(row) for row in list(first_payload.get("renderables") or []) if isinstance(row, dict)]
    renderable_ids = [str(row.get("renderable_id", "")).strip() for row in renderables]
    if renderable_ids != sorted(renderable_ids):
        return {"status": "fail", "message": "interior overlay renderables are not sorted deterministically"}

    return {"status": "pass", "message": "interior overlay ordering deterministic"}

