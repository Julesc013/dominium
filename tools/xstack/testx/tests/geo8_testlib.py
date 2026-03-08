"""Shared deterministic GEO-8 worldgen fixtures for TestX."""

from __future__ import annotations

import copy

from src.geo import build_worldgen_request, worldgen_cache_clear
from tools.xstack.sessionx.common import identity_hash_for_payload
from tools.xstack.sessionx.process_runtime import execute_intent
from tools.xstack.testx.tests.mobility_free_testlib import (
    authority_context,
    law_profile,
    policy_context,
    seed_free_state,
)


ALLOWED_WORLDGEN_PROCESSES = ["process.worldgen_request"]


def worldgen_cell_key(index_tuple):
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r3_infinite",
        "chart_id": "chart.global.r3",
        "index_tuple": list(index_tuple),
        "refinement_level": 0,
        "extensions": {},
    }


def seed_worldgen_state():
    state = seed_free_state(initial_velocity_x=0)
    identity = {
        "schema_version": "1.0.0",
        "universe_id": "universe.test.geo8",
        "global_seed": "seed.geo8.fixture.001",
        "domain_binding_ids": ["domain.navigation", "domain.astronomy"],
        "physics_profile_id": "physics.null",
        "topology_profile_id": "geo.topology.r3_infinite",
        "metric_profile_id": "geo.metric.euclidean",
        "partition_profile_id": "geo.partition.grid_zd",
        "projection_profile_id": "geo.projection.perspective_3d",
        "generator_version_id": "gen.v0_stub",
        "realism_profile_id": "realism.realistic_default_milkyway_stub",
        "base_scenario_id": "scenario.lab.galaxy_nav",
        "initial_pack_set_hash_expectation": "d9eb253e069b2ce7fbbdb5f95f98cc28fbf3622f29227cececad2e89d13718a5",
        "compatibility_schema_refs": [
            "generator_version@1.0.0",
            "realism_profile@1.0.0",
            "space_topology_profile@1.0.0",
            "metric_profile@1.0.0",
            "partition_profile@1.0.0",
            "projection_profile@1.0.0",
            "universe_identity@1.0.0",
        ],
        "immutable_after_create": True,
        "extensions": {},
        "identity_hash": "",
    }
    identity["identity_hash"] = identity_hash_for_payload(identity)
    state["universe_identity"] = identity
    state["field_layers"] = []
    state["field_cells"] = []
    state["geometry_cell_states"] = []
    state["worldgen_requests"] = []
    state["worldgen_results"] = []
    state["worldgen_spawned_objects"] = []
    return state


def reset_worldgen_cache():
    worldgen_cache_clear()


def worldgen_contexts():
    return (
        copy.deepcopy(law_profile(ALLOWED_WORLDGEN_PROCESSES)),
        copy.deepcopy(authority_context()),
        copy.deepcopy(policy_context()),
    )


def worldgen_request_row(*, request_id: str, index_tuple, refinement_level: int = 2, reason: str = "query"):
    return build_worldgen_request(
        request_id=request_id,
        geo_cell_key=worldgen_cell_key(index_tuple),
        refinement_level=refinement_level,
        reason=reason,
        extensions={"source": "geo8_testlib"},
    )


def run_worldgen_process(*, state, request_row=None, index_tuple=None, refinement_level: int = 2, reason: str = "query"):
    law, auth, policy = worldgen_contexts()
    request = request_row or worldgen_request_row(
        request_id="worldgen.request.{}".format(len(list(state.get("worldgen_requests") or []))),
        index_tuple=index_tuple or [0, 0, 0],
        refinement_level=refinement_level,
        reason=reason,
    )
    intent = {
        "intent_id": "intent.process.worldgen_request.{}".format(len(list(state.get("events") or []))),
        "process_id": "process.worldgen_request",
        "inputs": {
            "worldgen_request": dict(request),
        },
    }
    return execute_intent(
        state=state,
        intent=intent,
        law_profile=law,
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )
