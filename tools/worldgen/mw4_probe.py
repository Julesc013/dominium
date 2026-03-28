"""Deterministic MW-4 refinement pipeline probe helpers."""

from __future__ import annotations

import copy
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from client.ui.viewer_shell import build_viewer_shell_state  # noqa: E402
from worldgen.refinement.refinement_cache import build_refinement_cache_key  # noqa: E402
from worldgen.refinement.refinement_scheduler import build_refinement_request_record  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import execute_intent  # noqa: E402
from tools.xstack.testx.tests.geo8_testlib import reset_worldgen_cache, seed_worldgen_state, worldgen_cell_key  # noqa: E402
from tools.xstack.testx.tests.mobility_free_testlib import authority_context, law_profile, policy_context  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _viewer_perceived_model() -> dict:
    return {
        "viewpoint_id": "viewpoint.mw4.fixture",
        "camera_viewpoint": {"view_mode_id": "view.free.lab"},
        "time_state": {"tick": 12},
        "truth_overlay": {"state_hash_anchor": "truth.mw4.fixture.001"},
        "metadata": {
            "lens_type": "nondiegetic",
            "epistemic_policy_id": "epistemic.admin_full",
        },
        "channels": ["ch.diegetic.map_local"],
        "diegetic_instruments": {
            "instrument.map_local": {
                "reading": {
                    "entries": [
                        {
                            "cell_key": "placeholder",
                            "terrain_class": "macro",
                        }
                    ]
                }
            }
        },
    }


def seed_mw4_state() -> dict:
    reset_worldgen_cache()
    state = seed_worldgen_state()
    state["universe_identity"]["universe_contract_bundle_hash"] = "bundle.contract.mw4.fixture"
    state["universe_contract_bundle_hash"] = "bundle.contract.mw4.fixture"
    state["overlay_manifest_hash"] = "overlay.mw4.fixture"
    state["mod_policy_id"] = "mod_policy.strict"
    state["refinement_request_records"] = []
    state["refinement_cache_entries"] = []
    state["refinement_deferred_rows"] = []
    state["refinement_queue_capacity"] = 8
    state["refinement_cost_units"] = 1
    return state


def mw4_contexts(*, max_compute_units_per_tick: int = 4):
    allowed = [
        "process.refinement_request_enqueue",
        "process.refinement_scheduler_tick",
        "process.worldgen_request",
    ]
    return (
        copy.deepcopy(law_profile(allowed)),
        copy.deepcopy(authority_context()),
        copy.deepcopy(policy_context(max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick))))),
    )


def refinement_request_for(
    *,
    request_id: str,
    request_kind: str,
    index_tuple: list[int],
    refinement_level: int,
    priority_class: str,
    tick: int = 0,
) -> dict:
    return build_refinement_request_record(
        request_id=str(request_id),
        request_kind=str(request_kind),
        geo_cell_key=worldgen_cell_key(index_tuple),
        refinement_level=int(refinement_level),
        priority_class=str(priority_class),
        tick=int(tick),
        extensions={"source": "mw4_probe"},
    )


def enqueue_refinement_request(*, state: dict, request_row: Mapping[str, object]) -> dict:
    law, auth, policy = mw4_contexts(max_compute_units_per_tick=2)
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.{}".format(str(_as_map(request_row).get("request_id", "")).strip() or canonical_sha256(request_row)[:16]),
            "process_id": "process.refinement_request_enqueue",
            "inputs": {"refinement_request_record": dict(request_row)},
        },
        law_profile=law,
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )


def run_refinement_scheduler_tick(*, state: dict, max_compute_units_per_tick: int) -> dict:
    law, auth, policy = mw4_contexts(max_compute_units_per_tick=max_compute_units_per_tick)
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.process.refinement_scheduler_tick.{}".format(len(list(state.get("worldgen_results") or []))),
            "process_id": "process.refinement_scheduler_tick",
            "inputs": {
                "queue_capacity": int(state.get("refinement_queue_capacity", 8) or 8),
                "refinement_cost_units": int(state.get("refinement_cost_units", 1) or 1),
            },
        },
        law_profile=law,
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )


def build_mw4_viewer_state(*, state: Mapping[str, object] | None, teleport_command: str = "/tp sol") -> dict:
    runtime_state = _as_map(state)
    return build_viewer_shell_state(
        repo_root=REPO_ROOT_HINT,
        seed="42",
        authority_mode="dev",
        entrypoint="client",
        ui_mode="gui",
        start_session=True,
        perceived_model=_viewer_perceived_model(),
        requested_lens_profile_id="lens.freecam",
        teleport_command=str(teleport_command),
        map_layer_ids=["layer.terrain_stub", "layer.refinement_status"],
        minimap_layer_ids=["layer.terrain_stub", "layer.refinement_status"],
        extensions={
            "refinement_request_records": list(runtime_state.get("refinement_request_records") or []),
            "worldgen_results": list(runtime_state.get("worldgen_results") or []),
            "refinement_cache_entries": list(runtime_state.get("refinement_cache_entries") or []),
            "refinement_deferred_rows": list(runtime_state.get("refinement_deferred_rows") or []),
        },
    )


def run_refinement_stress(repo_root: str = REPO_ROOT_HINT) -> dict:
    del repo_root
    state = seed_mw4_state()
    initial_viewer = build_mw4_viewer_state(state=state)
    region_cell_keys = list(_as_map(_as_map(initial_viewer.get("refinement_surface")).get("status_view")).get("cell_keys") or [])
    target_cells = [dict(row) for row in region_cell_keys[:5] if isinstance(row, Mapping)]
    while len(target_cells) < 5:
        target_cells.append(worldgen_cell_key([800 + len(target_cells), 0, 0]))
    request_rows = [
        build_refinement_request_record(
            request_id="refinement.fixture.teleport",
            request_kind="teleport",
            geo_cell_key=target_cells[0],
            refinement_level=2,
            priority_class="priority.teleport.destination",
            tick=0,
            extensions={"source": "mw4_probe"},
        ),
        build_refinement_request_record(
            request_id="refinement.fixture.roi.current.0",
            request_kind="roi",
            geo_cell_key=target_cells[1],
            refinement_level=0,
            priority_class="priority.roi.current",
            tick=0,
            extensions={"source": "mw4_probe"},
        ),
        build_refinement_request_record(
            request_id="refinement.fixture.inspect",
            request_kind="inspect",
            geo_cell_key=target_cells[2],
            refinement_level=2,
            priority_class="priority.inspect.focus",
            tick=0,
            extensions={"source": "mw4_probe"},
        ),
        build_refinement_request_record(
            request_id="refinement.fixture.roi.current.1",
            request_kind="roi",
            geo_cell_key=target_cells[3],
            refinement_level=0,
            priority_class="priority.roi.current",
            tick=0,
            extensions={"source": "mw4_probe"},
        ),
        build_refinement_request_record(
            request_id="refinement.fixture.path",
            request_kind="path",
            geo_cell_key=target_cells[4],
            refinement_level=1,
            priority_class="priority.path.current",
            tick=0,
            extensions={"source": "mw4_probe"},
        ),
    ]
    enqueue_results = [enqueue_refinement_request(state=state, request_row=row) for row in request_rows]
    viewer_before = build_mw4_viewer_state(state=state)
    first_tick = run_refinement_scheduler_tick(state=state, max_compute_units_per_tick=2)
    viewer_after_first = build_mw4_viewer_state(state=state)
    remaining_after_first_tick = [str(row.get("request_id", "")) for row in list(state.get("refinement_request_records") or [])]
    first_tick_hashes = {
        "worldgen_result_hash_chain": str(state.get("worldgen_result_hash_chain", "")).strip(),
        "refinement_request_hash_chain": str(state.get("refinement_request_hash_chain", "")).strip(),
        "refinement_cache_hash_chain": str(state.get("refinement_cache_hash_chain", "")).strip(),
    }
    second_tick = run_refinement_scheduler_tick(state=state, max_compute_units_per_tick=8)
    viewer_after_second = build_mw4_viewer_state(state=state)
    cache_entries = list(state.get("refinement_cache_entries") or [])
    contract_bundle_hash = str(state.get("universe_contract_bundle_hash", "")).strip()
    overlay_manifest_hash = str(state.get("overlay_manifest_hash", "")).strip()
    mod_policy_id = str(state.get("mod_policy_id", "")).strip()
    cache_key_example = build_refinement_cache_key(
        universe_identity_hash=str(_as_map(state.get("universe_identity")).get("identity_hash", "")).strip(),
        universe_contract_bundle_hash=contract_bundle_hash,
        generator_version_id=str(_as_map(state.get("universe_identity")).get("generator_version_id", "")).strip(),
        realism_profile_id=str(_as_map(state.get("universe_identity")).get("realism_profile_id", "")).strip(),
        overlay_manifest_hash=overlay_manifest_hash,
        mod_policy_id=mod_policy_id,
        geo_cell_key=target_cells[0],
        refinement_level=2,
    )
    report = {
        "result": "complete",
        "enqueue_results": [str(item.get("result", "")) for item in enqueue_results],
        "approved_first_tick": [
            str(row.get("request_id", ""))
            for row in list((first_tick.get("scheduler_results") or _as_map(first_tick.get("result_metadata")).get("scheduler_results") or []))
        ],
        "remaining_after_first_tick": remaining_after_first_tick,
        "first_tick_hashes": first_tick_hashes,
        "second_tick_result": str(second_tick.get("result", "")).strip(),
        "final_queue_size": int(len(list(state.get("refinement_request_records") or []))),
        "worldgen_result_hash_chain": str(state.get("worldgen_result_hash_chain", "")).strip(),
        "worldgen_spawned_object_hash_chain": str(state.get("worldgen_spawned_object_hash_chain", "")).strip(),
        "refinement_request_hash_chain": str(state.get("refinement_request_hash_chain", "")).strip(),
        "refinement_cache_hash_chain": str(state.get("refinement_cache_hash_chain", "")).strip(),
        "refinement_deferred_hash_chain": str(state.get("refinement_deferred_hash_chain", "")).strip(),
        "overlay_manifest_hash": overlay_manifest_hash,
        "universe_contract_bundle_hash": contract_bundle_hash,
        "mod_policy_id": mod_policy_id,
        "cache_entry_count": int(len(cache_entries)),
        "cache_key_example": cache_key_example,
        "cache_key_present": bool(
            cache_key_example
            in set(str(_as_map(row).get("cache_key", "")).strip() for row in cache_entries if isinstance(row, Mapping))
        ),
        "stress_target_cells": [dict(row) for row in target_cells],
        "viewer_before_status": dict(_as_map(_as_map(viewer_before.get("refinement_surface")).get("status_view"))),
        "viewer_after_first_status": dict(_as_map(_as_map(viewer_after_first.get("refinement_surface")).get("status_view"))),
        "viewer_after_second_status": dict(_as_map(_as_map(viewer_after_second.get("refinement_surface")).get("status_view"))),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_refinement_window_replay(repo_root: str = REPO_ROOT_HINT) -> dict:
    first = run_refinement_stress(repo_root)
    second = run_refinement_stress(repo_root)
    stable = canonical_sha256(first) == canonical_sha256(second)
    return {
        "result": "complete" if stable else "refused",
        "stable": bool(stable),
        "first_report": first,
        "second_report": second,
        "deterministic_fingerprint": canonical_sha256({"first": first, "second": second}),
    }


__all__ = [
    "build_mw4_viewer_state",
    "enqueue_refinement_request",
    "mw4_contexts",
    "refinement_request_for",
    "run_refinement_scheduler_tick",
    "run_refinement_stress",
    "seed_mw4_state",
    "verify_refinement_window_replay",
]
