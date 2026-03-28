"""Shared deterministic GEO-7 geometry edit fixtures for TestX."""

from __future__ import annotations

import copy

from geo import build_geometry_cell_state, geometry_get_cell_state
from materials import create_material_batch
from tools.xstack.sessionx.process_runtime import execute_intent
from tools.xstack.testx.tests.mobility_free_testlib import (
    authority_context,
    law_profile,
    policy_context,
    seed_free_state,
)


ALLOWED_GEOMETRY_PROCESSES = [
    "process.geometry_remove",
    "process.geometry_add",
    "process.geometry_replace",
    "process.geometry_cut",
]


def geometry_cell_key(index_tuple):
    return {
        "partition_profile_id": "geo.partition.grid_zd",
        "topology_profile_id": "geo.topology.r3_infinite",
        "chart_id": "chart.global.r3",
        "index_tuple": list(index_tuple),
        "refinement_level": 0,
        "extensions": {},
    }


def seed_geometry_state():
    state = seed_free_state(initial_velocity_x=0)
    state["geometry_cell_states"] = [
        build_geometry_cell_state(
            geo_cell_key=geometry_cell_key([0, 0, 0]),
            material_id="material.stone_basic",
            occupancy_fraction=1000,
        ),
        build_geometry_cell_state(
            geo_cell_key=geometry_cell_key([1, 0, 0]),
            material_id="material.stone_basic",
            occupancy_fraction=1000,
        ),
    ]
    state["material_batches"] = [
        create_material_batch(
            material_id="material.stone_basic",
            quantity_mass_raw=600,
            origin_process_id="process.seed",
            origin_tick=0,
        )
    ]
    return state


def geometry_contexts():
    return (
        copy.deepcopy(law_profile(ALLOWED_GEOMETRY_PROCESSES)),
        copy.deepcopy(authority_context()),
        copy.deepcopy(policy_context()),
    )


def run_geometry_process(*, state, process_id, inputs):
    law, auth, policy = geometry_contexts()
    intent = {
        "intent_id": "intent.{}.{}".format(process_id.replace(".", "_"), len(list(state.get("events") or []))),
        "process_id": process_id,
        "inputs": dict(inputs),
    }
    return execute_intent(
        state=state,
        intent=intent,
        law_profile=law,
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )


def geometry_cell_row(state, index_tuple):
    return geometry_get_cell_state(geometry_cell_key(index_tuple), state.get("geometry_cell_states"))
