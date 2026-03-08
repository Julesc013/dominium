"""FAST test: POLL dispersion routes neighborhood lookup through GEO neighbors."""

from __future__ import annotations

import sys


TEST_ID = "test_poll_dispersion_uses_geo_neighbors"
TEST_TAGS = ["fast", "pollution", "geo"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    import src.pollution.dispersion_engine as dispersion_engine
    from src.fields import build_field_cell

    calls = []
    original = dispersion_engine.geo_neighbors

    def _tracking_geo_neighbors(*args, **kwargs):
        calls.append({"args": list(args), "kwargs": dict(kwargs)})
        return original(*args, **kwargs)

    dispersion_engine.geo_neighbors = _tracking_geo_neighbors
    try:
        result = dispersion_engine.evaluate_pollution_dispersion(
            current_tick=4,
            pollutant_types_by_id={
                "pollutant.smoke_particulate": {
                    "pollutant_id": "pollutant.smoke_particulate",
                    "default_dispersion_policy_id": "poll.policy.coarse_diffuse",
                    "default_decay_model_id": "model.poll_decay_none",
                    "extensions": {},
                }
            },
            pollution_policies_by_id={
                "poll.policy.coarse_diffuse": {
                    "policy_id": "poll.policy.coarse_diffuse",
                    "tier": "P1",
                    "wind_modifier_enabled": False,
                    "extensions": {
                        "topology_profile_id": "geo.topology.r2_infinite",
                        "metric_profile_id": "geo.metric.euclidean",
                        "partition_profile_id": "geo.partition.grid_zd",
                        "neighbor_radius": 1,
                    },
                }
            },
            decay_models_by_id={
                "model.poll_decay_none": {
                    "model_id": "model.poll_decay_none",
                    "kind": "none",
                    "extensions": {},
                }
            },
            pollution_source_event_rows=[
                {
                    "source_event_id": "source.poll.geo.001",
                    "tick": 4,
                    "pollutant_id": "pollutant.smoke_particulate",
                    "emitted_mass": 25,
                    "spatial_scope_id": "cell.0.0",
                }
            ],
            processed_source_event_ids=[],
            field_cell_rows=[
                build_field_cell(
                    field_id="field.pollution.smoke_particulate_concentration",
                    cell_id="cell.0.0",
                    value=10,
                    last_updated_tick=0,
                ),
                build_field_cell(
                    field_id="field.wind",
                    cell_id="cell.0.0",
                    value={"x": 0, "y": 0, "z": 0},
                    value_kind="vector",
                    last_updated_tick=0,
                ),
            ],
            neighbor_map_by_cell={},
            wind_field_id="field.wind",
            max_cell_updates_per_tick=16,
        )
    finally:
        dispersion_engine.geo_neighbors = original

    if not calls:
        return {"status": "fail", "message": "pollution dispersion did not call geo_neighbors"}
    if str(result.get("degrade_reason", "")) not in {"", "None"} and "degrade" in str(result.get("degrade_reason", "")):
        return {"status": "fail", "message": "pollution dispersion unexpectedly degraded in GEO-neighbor test"}
    first = dict(calls[0])
    if not first.get("args") or str(first["args"][0]) != "cell.0.0":
        return {"status": "fail", "message": "pollution dispersion did not query GEO neighbors for the expected cell"}
    return {"status": "pass", "message": "pollution dispersion uses GEO neighbors"}

