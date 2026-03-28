"""Shared POLL-1 dispersion TestX fixtures."""

from __future__ import annotations

import copy
import sys
from typing import Iterable, Mapping


def _sorted_tokens(values: Iterable[object]) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def build_pollution_field_inputs(
    *,
    repo_root: str,
    pollutant_id: str,
    cell_ids: list[str],
    reverse_order: bool = False,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fields import build_field_cell, build_field_layer
    from pollution.dispersion_engine import concentration_field_id_for_pollutant

    pollutant_token = str(pollutant_id).strip()
    concentration_field_id = str(concentration_field_id_for_pollutant(pollutant_token))
    ordered_cells = list(_sorted_tokens(cell_ids))
    if reverse_order:
        ordered_cells = list(reversed(ordered_cells))

    layers = [
        build_field_layer(
            field_id=concentration_field_id,
            field_type_id=concentration_field_id,
            spatial_scope_id="spatial.pollution.test",
            resolution_level="macro",
            update_policy_id="field.pollution_profile_defined",
            extensions={},
        ),
        build_field_layer(
            field_id="field.wind",
            field_type_id="field.wind",
            spatial_scope_id="spatial.pollution.test",
            resolution_level="macro",
            update_policy_id="field.static",
            extensions={},
        ),
    ]
    cells = []
    for cell_id in ordered_cells:
        cells.append(
            build_field_cell(
                field_id=concentration_field_id,
                cell_id=cell_id,
                value=0,
                last_updated_tick=0,
                value_kind="scalar",
            )
        )
        cells.append(
            build_field_cell(
                field_id="field.wind",
                cell_id=cell_id,
                value={"x": 0, "y": 0, "z": 0},
                last_updated_tick=0,
                value_kind="vector",
            )
        )
    neighbor_map = {}
    for index, cell_id in enumerate(ordered_cells):
        neighbors = []
        if index > 0:
            neighbors.append(ordered_cells[index - 1])
        if index + 1 < len(ordered_cells):
            neighbors.append(ordered_cells[index + 1])
        neighbor_map[cell_id] = list(_sorted_tokens(neighbors))
    return {
        "field_layers": [dict(row) for row in layers if isinstance(row, dict)],
        "field_cells": [dict(row) for row in cells if isinstance(row, dict)],
        "neighbor_map_by_cell": dict((key, list(neighbor_map[key])) for key in sorted(neighbor_map.keys())),
    }


def seed_state_with_pollution_emission(
    *,
    repo_root: str,
    pollutant_id: str,
    emitted_mass: int,
    source_cell_id: str,
    origin_kind: str = "reaction",
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_testlib import execute_pollution_emit, seed_pollution_state

    state = seed_pollution_state()
    emit_out = execute_pollution_emit(
        repo_root=repo_root,
        state=state,
        inputs={
            "policy_id": "poll.policy.coarse_diffuse",
            "events": [
                {
                    "origin_kind": str(origin_kind),
                    "origin_id": "event.pollution.seed.{}".format(str(pollutant_id).replace(".", "_")),
                    "pollutant_id": str(pollutant_id),
                    "emitted_mass": int(max(0, int(emitted_mass))),
                    "spatial_scope_id": str(source_cell_id),
                }
            ],
        },
    )
    if str(emit_out.get("result", "")).strip() != "complete":
        raise RuntimeError("pollution emit seed failed: {}".format(emit_out))
    return state


def execute_pollution_dispersion_tick(
    *,
    repo_root: str,
    state: dict,
    inputs: Mapping[str, object] | None = None,
    policy_overrides: Mapping[str, object] | None = None,
    max_compute_units_per_tick: int = 4096,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context as construction_authority_context,
        law_profile as construction_law_profile,
        policy_context as construction_policy_context,
    )

    law = construction_law_profile(["process.pollution_dispersion_tick"])
    authority = construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect"],
        privilege_level="operator",
    )
    policy = construction_policy_context(
        max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick)))
    )
    if isinstance(policy_overrides, Mapping):
        for key, value in dict(policy_overrides).items():
            policy[str(key)] = copy.deepcopy(value)

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.pollution.dispersion.test",
            "process_id": "process.pollution_dispersion_tick",
            "inputs": dict(inputs or {}),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
