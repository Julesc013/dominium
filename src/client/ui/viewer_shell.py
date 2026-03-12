"""Deterministic UX-0 viewer shell state machine over derived artifacts only."""

from __future__ import annotations

from typing import Mapping

from src.client.render import build_render_model
from src.embodiment import (
    build_cut_trench_task,
    build_fill_at_cursor_task,
    build_logic_probe_task,
    build_logic_trace_task,
    build_mine_at_cursor_task,
    build_scan_result,
    build_teleport_tool_surface,
    build_toolbelt_availability_surface,
    resolve_authorized_lens_profile,
    resolve_lens_camera_state,
    resolve_smoothed_camera_state,
)
from src.client.ui.inspect_panels import build_inspection_panel_set
from src.client.ui.map_views import build_map_view_set, debug_view_limit_for_compute_profile
from src.geo import build_position_ref
from src.worldgen.earth.lighting import build_lighting_view_surface
from src.worldgen.earth.sky import build_sky_view_surface
from src.worldgen.earth.water import build_water_layer_source_payloads, build_water_view_surface
from src.worldgen.refinement.refinement_scheduler import (
    build_refinement_layer_source_payloads,
    build_refinement_request_record,
    build_refinement_status_view,
    normalize_refinement_request_record_rows,
)
from tools.mvp.runtime_bundle import (
    MVP_PACK_LOCK_REL,
    MVP_PROFILE_BUNDLE_REL,
    build_runtime_bootstrap,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


STATE_BOOT = "Boot"
STATE_BUNDLE_SELECT = "BundleSelect"
STATE_SEED_SELECT = "SeedSelect"
STATE_SESSION_RUNNING = "SessionRunning"
DEFAULT_VIEWER_LENS_PROFILE_ID = "lens.fp"


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_bool(value: object, default_value: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        token = value.strip().lower()
        if token in ("1", "true", "yes", "on"):
            return True
        if token in ("0", "false", "no", "off"):
            return False
    return bool(default_value)


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_strings(values: object) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _ordered_strings(values: object) -> list[str]:
    out: list[str] = []
    for item in list(values or []):
        token = str(item).strip()
        if token and token not in out:
            out.append(token)
    return out


def _vector3_int(value: object) -> dict:
    payload = _as_map(value)
    return {
        "x": int(_as_int(payload.get("x", 0), 0)),
        "y": int(_as_int(payload.get("y", 0), 0)),
        "z": int(_as_int(payload.get("z", 0), 0)),
    }


def _has_signal(value: object) -> bool:
    vector = _vector3_int(value)
    return bool(int(vector["x"]) or int(vector["y"]) or int(vector["z"]))


def _entitlements(authority_context: Mapping[str, object] | None) -> set[str]:
    return set(_ordered_strings(_as_map(authority_context).get("entitlements")))


def _truth_hash_anchor(perceived_model: Mapping[str, object] | None) -> str:
    return str(_as_map(_as_map(perceived_model).get("truth_overlay")).get("state_hash_anchor", "")).strip()


def _tool_requests(extensions: Mapping[str, object] | None) -> dict:
    return _as_map(_as_map(extensions).get("tool_requests"))


def _worldgen_star_artifact_rows(extensions: Mapping[str, object] | None) -> list[dict]:
    return [dict(row) for row in list(_as_map(extensions).get("worldgen_star_artifacts") or []) if isinstance(row, Mapping)]


def _worldgen_planet_basic_artifact_rows(extensions: Mapping[str, object] | None) -> list[dict]:
    return [dict(row) for row in list(_as_map(extensions).get("worldgen_planet_basic_artifacts") or []) if isinstance(row, Mapping)]


def _universe_identity_from_bootstrap(bootstrap: Mapping[str, object] | None) -> dict:
    session_spec = _as_map(_as_map(bootstrap).get("session_spec"))
    profile_bundle = _as_map(_as_map(bootstrap).get("profile_bundle"))
    return {
        "universe_seed": str(session_spec.get("universe_seed", "")).strip(),
        "generator_version_id": str(session_spec.get("generator_version_id", "")).strip(),
        "realism_profile_id": str(session_spec.get("realism_profile_id", "")).strip(),
        "profile_bundle_id": str(profile_bundle.get("profile_bundle_id", "")).strip(),
    }


def _preferred_position_ref(
    *,
    explicit_position_ref: Mapping[str, object] | None,
    selection: Mapping[str, object] | None,
) -> dict:
    if _as_map(explicit_position_ref):
        return _as_map(explicit_position_ref)
    selected = _as_map(selection)
    for key in ("position_ref", "origin_position_ref", "camera_position_ref"):
        candidate = _as_map(selected.get(key))
        if candidate:
            return candidate
    return {}


def _default_authority_context(authority_mode: str) -> dict:
    mode = str(authority_mode or "").strip().lower() or "dev"
    entitlements = ["session.boot", "entitlement.control.camera", "entitlement.control.possess", "ent.move.jump"]
    if mode == "dev":
        entitlements.extend(
            [
                "entitlement.admin",
                "entitlement.control.admin",
                "lens.nondiegetic.access",
                "entitlement.control.lens_override",
                "entitlement.inspect",
                "entitlement.debug_view",
                "entitlement.teleport",
                "entitlement.tool.equip",
                "entitlement.tool.use",
                "entitlement.observer.truth",
                "ent.tool.terrain_edit",
                "ent.tool.scan",
                "ent.tool.logic_probe",
                "ent.tool.logic_trace",
                "ent.tool.teleport",
            ]
        )
    else:
        entitlements.extend(
            [
                "entitlement.tool.equip",
                "entitlement.tool.use",
                "ent.tool.scan",
            ]
        )
    return {
        "authority_origin": "client" if mode == "release" else "tool",
        "law_profile_id": "law.softcore_observer" if mode == "release" else "law.lab_freecam",
        "entitlements": sorted(set(entitlements)),
        "epistemic_scope": {
            "scope_id": "epistemic.diegetic_default" if mode == "release" else "epistemic.admin_full",
            "visibility_level": "diegetic" if mode == "release" else "nondiegetic",
        },
        "privilege_level": "observer" if mode == "release" else "operator",
    }


def _resolve_active_lens_resolution(
    *,
    requested_lens_profile_id: str,
    authority_context: Mapping[str, object] | None,
    available_lens_profile_ids: object,
) -> dict:
    requested = str(requested_lens_profile_id or "").strip() or DEFAULT_VIEWER_LENS_PROFILE_ID
    attempts = []
    for candidate in _ordered_strings([requested] + list(available_lens_profile_ids or [])):
        result = resolve_authorized_lens_profile(
            requested_lens_profile_id=str(candidate),
            authority_context=authority_context,
        )
        attempts.append(
            {
                "lens_profile_id": str(candidate),
                "result": str(result.get("result", "")).strip() or "refused",
                "reason_code": str(result.get("reason_code", "")).strip(),
            }
        )
        if str(result.get("result", "")).strip() == "complete":
            payload = {
                "result": "complete",
                "requested_lens_profile_id": requested,
                "active_lens_profile_id": str(candidate),
                "fallback_applied": bool(str(candidate) != requested),
                "lens_profile": dict(result.get("lens_profile") or {}),
                "attempt_trace": list(attempts),
                "deterministic_fingerprint": "",
            }
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
            return payload
    payload = {
        "result": "refused",
        "requested_lens_profile_id": requested,
        "active_lens_profile_id": "",
        "fallback_applied": False,
        "attempt_trace": list(attempts),
        "reason_code": "refusal.view.lens_profile_invalid",
        "message": "no authorized lens profile is available",
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _camera_position_ref(
    *,
    camera_state: Mapping[str, object] | None,
    body_state: Mapping[str, object] | None,
    lens_id: str,
) -> dict:
    state = _as_map(camera_state)
    if "position_mm" not in state:
        return {}
    position_mm = _vector3_int(state.get("position_mm"))
    return build_position_ref(
        object_id="camera.main",
        frame_id=str(_as_map(body_state).get("frame_id", "")).strip() or "frame.surface_local",
        local_position=[int(position_mm["x"]), int(position_mm["y"]), int(position_mm["z"])],
        extensions={"source": "UX0-6", "lens_id": str(lens_id or "").strip() or None},
    )


def _next_authorized_lens(
    *,
    current_lens_profile_id: str,
    toggle_sequence: object,
    authority_context: Mapping[str, object] | None,
) -> dict:
    sequence = _ordered_strings(toggle_sequence)
    current = str(current_lens_profile_id or "").strip() or DEFAULT_VIEWER_LENS_PROFILE_ID
    if not sequence:
        sequence = [current]
    if current not in sequence:
        sequence = [current] + sequence
    start_index = sequence.index(current)
    for offset in range(1, len(sequence) + 1):
        candidate = sequence[(start_index + offset) % len(sequence)]
        resolution = resolve_authorized_lens_profile(
            requested_lens_profile_id=candidate,
            authority_context=authority_context,
        )
        if str(resolution.get("result", "")).strip() == "complete":
            payload = {
                "result": "complete",
                "target_lens_profile_id": candidate,
                "lens_profile": dict(resolution.get("lens_profile") or {}),
                "deterministic_fingerprint": "",
            }
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
            return payload
    payload = {
        "result": "refused",
        "target_lens_profile_id": current,
        "reason_code": "refusal.view.lens_profile_invalid",
        "message": "no authorized lens is available in toggle sequence",
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _debug_controls(
    *,
    authority_context: Mapping[str, object] | None,
    requested_debug_view_ids: object,
    compute_profile_id: str,
) -> dict:
    entitlements = _entitlements(authority_context)
    allowed = []
    if "entitlement.inspect" in entitlements:
        allowed.append("inspect.overlay_provenance")
    if "entitlement.debug_view" in entitlements:
        allowed.extend(
            [
                "viewer.object_ids",
                "viewer.field_layers",
                "viewer.geometry_layer",
                "viewer.truth_anchor_hash",
            ]
        )
    requested = [token for token in _ordered_strings(requested_debug_view_ids) if token in set(allowed)]
    max_active = int(debug_view_limit_for_compute_profile(str(compute_profile_id or "compute.default").strip() or "compute.default"))
    active = list(requested[:max_active])
    payload = {
        "allowed_debug_view_ids": list(allowed),
        "active_debug_view_ids": list(active),
        "throttled_debug_view_ids": list(requested[max_active:]),
        "compute_profile_id": str(compute_profile_id or "compute.default").strip() or "compute.default",
        "profile_gated": True,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _terrain_debug_overlay(
    *,
    authority_context: Mapping[str, object] | None,
    body_state: Mapping[str, object] | None,
    selection: Mapping[str, object] | None,
) -> dict:
    entitlements = _entitlements(authority_context)
    if "entitlement.debug_view" not in entitlements:
        payload = {
            "visible": False,
            "profile_gated": True,
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    state_ext = _as_map(_as_map(body_state).get("extensions"))
    collision = _as_map(state_ext.get("terrain_collision_state"))
    slope = _as_map(state_ext.get("terrain_slope_response"))
    locomotion = _as_map(state_ext.get("locomotion_state"))
    selected_surface = _as_map(_as_map(selection).get("surface_tile_artifact"))
    payload = {
        "visible": bool(collision or slope or selected_surface),
        "profile_gated": True,
        "terrain_height_mm": collision.get("terrain_height_mm"),
        "grounded": collision.get("grounded"),
        "jump_cooldown_remaining_ticks": locomotion.get("jump_cooldown_remaining_ticks"),
        "last_impact_speed": locomotion.get("last_impact_speed"),
        "slope_angle_mdeg": collision.get("slope_angle_mdeg") or slope.get("slope_angle_mdeg"),
        "selected_height_proxy": _as_int(_as_map(selected_surface.get("elevation_params_ref")).get("height_proxy", 0), 0)
        if selected_surface
        else None,
        "source_kind": "derived.viewer_shell",
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _build_control_surface(
    *,
    bootstrap: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
    lens_resolution: Mapping[str, object] | None,
    body_state: Mapping[str, object] | None,
    body_row: Mapping[str, object] | None,
    previous_camera_state: Mapping[str, object] | None,
    controller_id: str,
    move_vector_local: Mapping[str, object] | None,
    look_vector: Mapping[str, object] | None,
    jump_requested: bool,
    toggle_lens: bool,
    requested_debug_view_ids: object,
    compute_profile_id: str,
) -> dict:
    bootstrap_payload = _as_map(bootstrap)
    embodiment = _as_map(bootstrap_payload.get("embodiment"))
    lens_profile = _as_map(_as_map(lens_resolution).get("lens_profile"))
    lens_id = str(lens_profile.get("lens_id", "")).strip()
    entitlements = _entitlements(authority_context)
    camera_state_result = (
        resolve_lens_camera_state(
            body_state_row=body_state,
            body_row=body_row,
            lens_profile_row=lens_profile,
            previous_camera_state=previous_camera_state,
        )
        if lens_profile
        else {"result": "complete", "camera_state": dict(_as_map(previous_camera_state))}
    )
    camera_state = _as_map(camera_state_result.get("camera_state"))
    smoothed_camera_result = resolve_smoothed_camera_state(
        target_camera_state=camera_state,
        previous_camera_state=previous_camera_state,
        lens_profile_row=lens_profile,
    )
    render_camera_state = _as_map(smoothed_camera_result.get("camera_state")) or dict(camera_state)
    resolved_controller_id = str(controller_id or "").strip() or str(_as_map(authority_context).get("controller_id", "")).strip()
    resolved_controller_id = resolved_controller_id or "controller.local"
    body_id = str(_as_map(body_row).get("assembly_id", "")).strip() or str(_as_map(body_row).get("body_id", "")).strip()
    locomotion_state = _as_map(_as_map(body_state).get("extensions")).get("locomotion_state")
    locomotion_state = _as_map(locomotion_state)
    process_sequence = []
    jump_allowed = bool(
        body_id
        and "entitlement.control.possess" in entitlements
        and "ent.move.jump" in entitlements
    )
    if bool(jump_requested) and jump_allowed:
        process_sequence.append(
            {
                "process_id": "process.body_jump",
                "inputs": {
                    "body_id": body_id,
                    "controller_id": resolved_controller_id,
                    "dt_ticks": 1,
                },
            }
        )
    if body_id and "entitlement.control.possess" in entitlements and (_has_signal(move_vector_local) or _has_signal(look_vector)):
        process_sequence.append(
            {
                "process_id": "process.body_apply_input",
                "inputs": {
                    "body_id": body_id,
                    "controller_id": resolved_controller_id,
                    "move_vector_local": _vector3_int(move_vector_local),
                    "look_vector": _vector3_int(look_vector),
                    "dt_ticks": 1,
                },
            }
        )
    toggle_plan = {"result": "complete", "process_sequence": [], "target_lens_profile_id": ""}
    if bool(toggle_lens):
        next_lens = _next_authorized_lens(
            current_lens_profile_id=str(_as_map(lens_resolution).get("active_lens_profile_id", "")).strip()
            or str(lens_profile.get("lens_profile_id", "")).strip(),
            toggle_sequence=_as_map(bootstrap_payload.get("embodiment")).get("toggle_lens_sequence"),
            authority_context=authority_context,
        )
        target_profile = _as_map(next_lens.get("lens_profile"))
        if str(next_lens.get("result", "")).strip() == "complete" and target_profile:
            toggle_processes = [
                {
                    "process_id": "process.camera_set_view_mode",
                    "inputs": {
                        "controller_id": resolved_controller_id,
                        "camera_id": "camera.main",
                        "view_mode_id": str(target_profile.get("view_mode_id", "")).strip(),
                    },
                }
            ]
            target_lens_id = str(target_profile.get("lens_id", "")).strip()
            if target_lens_id and target_lens_id != lens_id:
                if "entitlement.control.lens_override" not in entitlements:
                    toggle_plan = {
                        "result": "refused",
                        "reason_code": "refusal.view.entitlement_missing",
                        "message": "lens override entitlement is required for nondiegetic lens changes",
                        "target_lens_profile_id": str(next_lens.get("target_lens_profile_id", "")).strip(),
                        "process_sequence": [],
                    }
                else:
                    toggle_processes.append(
                        {
                            "process_id": "process.camera_set_lens",
                            "inputs": {
                                "controller_id": resolved_controller_id,
                                "camera_id": "camera.main",
                                "lens_id": target_lens_id,
                            },
                        }
                    )
            if not toggle_plan.get("reason_code"):
                toggle_plan = {
                    "result": "complete",
                    "target_lens_profile_id": str(next_lens.get("target_lens_profile_id", "")).strip(),
                    "process_sequence": toggle_processes,
                }
        else:
            toggle_plan = {
                "result": "refused",
                "reason_code": str(next_lens.get("reason_code", "")).strip() or "refusal.view.lens_profile_invalid",
                "message": str(next_lens.get("message", "")).strip() or "no authorized target lens is available",
                "target_lens_profile_id": str(next_lens.get("target_lens_profile_id", "")).strip(),
                "process_sequence": [],
            }
    payload = {
        "result": "complete",
        "controller_id": resolved_controller_id,
        "camera_state": dict(render_camera_state),
        "camera_target_state": dict(camera_state),
        "camera_position_ref": _camera_position_ref(
            camera_state=render_camera_state,
            body_state=body_state,
            lens_id=lens_id,
        ),
        "input_bindings": dict(embodiment.get("input_bindings") or {}),
        "command_registry": {
            "commands": ["move jump"] if jump_allowed else [],
        },
        "jump_surface": {
            "available": bool(jump_allowed),
            "requested": bool(jump_requested),
            "grounded": bool(_as_map(_as_map(body_state).get("extensions")).get("terrain_collision_state", {}).get("grounded", False))
            if isinstance(_as_map(body_state).get("extensions"), Mapping)
            else False,
            "cooldown_remaining_ticks": int(max(0, _as_int(locomotion_state.get("jump_cooldown_remaining_ticks", 0), 0))),
            "required_entitlement_id": "ent.move.jump",
            "source_kind": "derived.viewer_control_surface",
        },
        "active_lens_profile_id": str(_as_map(lens_resolution).get("active_lens_profile_id", "")).strip()
        or str(lens_profile.get("lens_profile_id", "")).strip(),
        "active_lens_id": lens_id,
        "process_sequence": list(process_sequence),
        "lens_toggle_plan": dict(toggle_plan),
        "debug_controls": _debug_controls(
            authority_context=authority_context,
            requested_debug_view_ids=requested_debug_view_ids,
            compute_profile_id=compute_profile_id,
        ),
        "camera_smoothing": {
            "smoothing_applied": bool(smoothed_camera_result.get("smoothing_applied", False)),
            "camera_smoothing_params_id": str(smoothed_camera_result.get("camera_smoothing_params_id", "")).strip(),
            "deterministic_fingerprint": str(smoothed_camera_result.get("deterministic_fingerprint", "")).strip(),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _build_selection_controls(
    *,
    selection: Mapping[str, object] | None,
    map_views: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
) -> dict:
    entitlements = _entitlements(authority_context)
    candidate_geo_cell_keys = []
    seen = set()
    for view_key in ("minimap_view", "map_view"):
        rendered = list(_as_map(_as_map(_as_map(map_views).get(view_key)).get("projected_view_artifact")).get("rendered_cells") or [])
        for row in rendered:
            cell_key = _as_map(_as_map(row).get("geo_cell_key"))
            if not cell_key:
                continue
            cell_hash = canonical_sha256(cell_key)
            if cell_hash in seen:
                continue
            seen.add(cell_hash)
            candidate_geo_cell_keys.append(dict(cell_key))
    selected = _as_map(selection)
    payload = {
        "result": "complete",
        "selection_mode": "cell_list_stub",
        "inspect_allowed": bool("entitlement.inspect" in entitlements),
        "selected_object_id": str(selected.get("object_id", "")).strip() or str(selected.get("target_id", "")).strip(),
        "selected_geo_cell_key": dict(_as_map(selected.get("geo_cell_key"))),
        "candidate_geo_cell_keys": [dict(row) for row in candidate_geo_cell_keys[:32]],
        "raycast_stub_enabled": False,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _stage_trace(*, start_session: bool, seed: str, bundle_id: str) -> list[dict]:
    stages = [
        {
            "stage_id": STATE_BOOT,
            "status": "complete",
            "summary": "runtime bootstrap initialized",
        },
        {
            "stage_id": STATE_BUNDLE_SELECT,
            "status": "complete",
            "summary": "bundle selected {}".format(str(bundle_id or "profile.bundle.mvp_default")),
        },
        {
            "stage_id": STATE_SEED_SELECT,
            "status": "complete" if str(seed).strip() else "pending",
            "summary": "seed ready {}".format(str(seed or "<pending>")),
        },
        {
            "stage_id": STATE_SESSION_RUNNING,
            "status": "complete" if start_session else "pending",
            "summary": "session running" if start_session else "session not started",
        },
    ]
    return [dict(row) for row in stages]


def _current_stage(stage_trace: list[dict]) -> str:
    pending = [dict(row) for row in list(stage_trace or []) if str(dict(row).get("status", "")).strip() != "complete"]
    if pending:
        return str(dict(pending[0]).get("stage_id", STATE_BOOT))
    return STATE_SESSION_RUNNING


def _viewer_panels(current_stage: str) -> list[dict]:
    base = [
        {"panel_id": "viewer.session", "panel_kind": "session_summary"},
        {"panel_id": "viewer.render", "panel_kind": "render_summary"},
        {"panel_id": "viewer.sky", "panel_kind": "sky_summary"},
        {"panel_id": "viewer.inspect", "panel_kind": "inspection_summary"},
        {"panel_id": "viewer.map", "panel_kind": "map_summary"},
    ]
    visible = []
    for row in base:
        panel = dict(row)
        panel["visible"] = bool(current_stage == STATE_SESSION_RUNNING or panel["panel_id"] == "viewer.session")
        visible.append(panel)
    return visible


def _render_contract(
    *,
    perceived_model: Mapping[str, object] | None,
    registry_payloads: Mapping[str, object] | None,
    pack_lock_hash: str,
    camera_viewpoint_override: Mapping[str, object] | None = None,
    sky_view_artifact: Mapping[str, object] | None = None,
    illumination_view_artifact: Mapping[str, object] | None = None,
    water_view_artifact: Mapping[str, object] | None = None,
) -> dict:
    perceived = dict(_as_map(perceived_model))
    camera_override = _as_map(camera_viewpoint_override)
    if camera_override:
        perceived["camera_viewpoint"] = {
            **_as_map(perceived.get("camera_viewpoint")),
            **{
                "position_mm": _vector3_int(camera_override.get("position_mm")),
                "orientation_mdeg": {
                    "yaw": int(_as_int(_as_map(camera_override.get("orientation_mdeg")).get("yaw", 0), 0)),
                    "pitch": int(_as_int(_as_map(camera_override.get("orientation_mdeg")).get("pitch", 0), 0)),
                    "roll": int(_as_int(_as_map(camera_override.get("orientation_mdeg")).get("roll", 0), 0)),
                },
                "view_mode_id": str(camera_override.get("view_mode_id", "")).strip(),
                "lens_id": str(camera_override.get("lens_id", "")).strip(),
            },
        }
    if not perceived:
        return {
            "result": "complete",
            "render_model": {},
            "render_model_hash": "",
            "source_kind": "none",
        }
    render_result = build_render_model(
        perceived_model=perceived,
        registry_payloads=dict(registry_payloads or {}),
        pack_lock_hash=str(pack_lock_hash or ""),
        physics_profile_id="physics.default_realistic",
        sky_view_artifact=dict(sky_view_artifact or {}),
        illumination_view_artifact=dict(illumination_view_artifact or {}),
        water_view_artifact=dict(water_view_artifact or {}),
    )
    return {
        "result": str(render_result.get("result", "")) or "complete",
        "render_model": dict(render_result.get("render_model") or {}),
        "render_model_hash": str(render_result.get("render_model_hash", "")).strip(),
        "source_kind": "perceived.render_model",
    }


def _resolve_sky_observer_surface_artifact(
    *,
    selection: Mapping[str, object] | None,
    inspection_snapshot: Mapping[str, object] | None,
    layer_source_payloads: Mapping[str, object] | None,
    extensions: Mapping[str, object] | None,
) -> dict:
    candidates = [
        _as_map(_as_map(extensions).get("sky_observer_surface_artifact")),
        _as_map(_as_map(selection).get("surface_tile_artifact")),
        _as_map(_as_map(_as_map(_as_map(inspection_snapshot).get("target_payload")).get("row")).get("surface_tile_artifact")),
        _as_map(_as_map(_as_map(layer_source_payloads).get("layer.sky_dome")).get("observer_surface_artifact")),
        _as_map(_as_map(_as_map(layer_source_payloads).get("layer.starfield")).get("observer_surface_artifact")),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        ext = _as_map(candidate.get("extensions"))
        if ext.get("latitude_mdeg") is not None or candidate.get("tile_cell_key"):
            return dict(candidate)
    return {}


def _resolve_water_surface_tile_artifact_rows(
    *,
    selection: Mapping[str, object] | None,
    inspection_snapshot: Mapping[str, object] | None,
    extensions: Mapping[str, object] | None,
) -> list[dict]:
    rows = []
    candidates = [
        _as_map(_as_map(extensions).get("sky_observer_surface_artifact")),
        _as_map(_as_map(selection).get("surface_tile_artifact")),
        _as_map(_as_map(_as_map(_as_map(inspection_snapshot).get("target_payload")).get("row")).get("surface_tile_artifact")),
    ]
    for candidate in candidates:
        tile_id = str(candidate.get("tile_object_id", "")).strip()
        if tile_id:
            rows.append(dict(candidate))
    for raw in list(_as_map(extensions).get("surface_tile_artifact_rows") or []):
        row = _as_map(raw)
        tile_id = str(row.get("tile_object_id", "")).strip()
        if tile_id:
            rows.append(dict(row))
    deduped = {}
    for row in rows:
        deduped[str(row.get("tile_object_id", "")).strip()] = dict(row)
    return [dict(deduped[key]) for key in sorted(deduped.keys())]


def _resolve_water_tide_overlay_rows(
    *,
    selection: Mapping[str, object] | None,
    inspection_snapshot: Mapping[str, object] | None,
    field_values: Mapping[str, object] | None,
    extensions: Mapping[str, object] | None,
) -> list[dict]:
    rows = [
        dict(row)
        for row in list(_as_map(extensions).get("earth_tide_tile_overlays") or _as_map(extensions).get("tide_overlay_rows") or [])
        if isinstance(row, Mapping)
    ]
    if rows:
        return rows
    tide_value = _as_map(field_values).get("tide_height_proxy")
    if tide_value is None:
        return []
    surface_artifact = (
        _as_map(_as_map(selection).get("surface_tile_artifact"))
        or _as_map(_as_map(_as_map(_as_map(inspection_snapshot).get("target_payload")).get("row")).get("surface_tile_artifact"))
    )
    tile_id = str(surface_artifact.get("tile_object_id", "")).strip()
    tile_cell_key = _as_map(surface_artifact.get("tile_cell_key"))
    if not tile_id or not tile_cell_key:
        return []
    return [
        {
            "tile_object_id": tile_id,
            "tile_cell_key": dict(tile_cell_key),
            "tide_height_value": int(_as_int(tide_value, 0)),
        }
    ]


def _merge_layer_source_payloads(*, base: Mapping[str, object] | None, extra: Mapping[str, object] | None) -> dict:
    merged = dict((str(key), dict(_as_map(value))) for key, value in sorted(_as_map(base).items(), key=lambda item: str(item[0])))
    for key, value in sorted(_as_map(extra).items(), key=lambda item: str(item[0])):
        merged[str(key)] = dict(_as_map(value))
    return merged


def _refinement_level_for_view(*, observer_surface_artifact: Mapping[str, object] | None) -> int:
    return 3 if _as_map(observer_surface_artifact) else 0


def _viewer_generated_refinement_requests(
    *,
    preliminary_map_views: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None,
    selection: Mapping[str, object] | None,
    teleport_plan: Mapping[str, object] | None,
    current_tick: int,
    extensions: Mapping[str, object] | None,
) -> list[dict]:
    generated = []
    refinement_level = _refinement_level_for_view(observer_surface_artifact=observer_surface_artifact)
    for key in ("map_view", "minimap_view"):
        projected = _as_map(_as_map(_as_map(preliminary_map_views).get(key)).get("projected_view_artifact"))
        for rendered in list(projected.get("rendered_cells") or []):
            geo_cell_key = _as_map(_as_map(rendered).get("geo_cell_key"))
            if not geo_cell_key:
                continue
            generated.append(
                build_refinement_request_record(
                    request_id="refinement.request.{}".format(
                        canonical_sha256(
                            {
                                "source": "viewer.roi",
                                "geo_cell_key": geo_cell_key,
                                "refinement_level": refinement_level,
                            }
                        )[:16]
                    ),
                    request_kind="roi",
                    geo_cell_key=geo_cell_key,
                    refinement_level=refinement_level,
                    priority_class="priority.roi.current",
                    tick=int(max(0, _as_int(current_tick, 0))),
                    extensions={"source": "MW4-5", "origin": "viewer_shell"},
                )
            )
    selected_geo_cell_key = _as_map(_as_map(selection).get("geo_cell_key")) or _as_map(_as_map(observer_surface_artifact).get("tile_cell_key"))
    if selected_geo_cell_key:
        generated.append(
            build_refinement_request_record(
                request_id="refinement.request.{}".format(
                    canonical_sha256(
                        {
                            "source": "viewer.inspect",
                            "geo_cell_key": selected_geo_cell_key,
                            "refinement_level": refinement_level,
                        }
                    )[:16]
                ),
                request_kind="inspect",
                geo_cell_key=selected_geo_cell_key,
                refinement_level=refinement_level,
                priority_class="priority.inspect.focus",
                tick=int(max(0, _as_int(current_tick, 0))),
                extensions={"source": "MW4-5", "origin": "viewer_shell"},
            )
        )
    for process_row in list(_as_map(teleport_plan).get("process_sequence") or []):
        row = _as_map(process_row)
        if str(row.get("process_id", "")).strip() != "process.refinement_request_enqueue":
            continue
        generated.append(_as_map(_as_map(row.get("inputs")).get("refinement_request_record")))
    for raw in list(_as_map(extensions).get("path_request_records") or []):
        if isinstance(raw, Mapping):
            generated.append(dict(raw))
    return normalize_refinement_request_record_rows(generated)


def _surface_map_context(
    *,
    origin_position_ref: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None,
) -> tuple[dict, dict]:
    origin = _as_map(origin_position_ref)
    artifact = _as_map(observer_surface_artifact)
    tile_cell_key = _as_map(artifact.get("tile_cell_key"))
    if not origin or not tile_cell_key:
        return dict(origin), {}
    local_position = list(origin.get("local_position") or [])
    while len(local_position) < 3:
        local_position.append(0)
    augmented = build_position_ref(
        object_id=str(origin.get("object_id", "")).strip() or "camera.main",
        frame_id=str(origin.get("frame_id", "")).strip() or "frame.surface_local",
        local_position=[int(_as_int(item, 0)) for item in local_position[:3]],
        extensions={
            **_as_map(origin.get("extensions")),
            "chart_id": str(tile_cell_key.get("chart_id", "")).strip() or None,
            "geo_cell_key": dict(tile_cell_key),
        },
    )
    return (
        augmented,
        {
            "topology_profile_id": str(tile_cell_key.get("topology_profile_id", "")).strip() or "geo.topology.r3_infinite",
            "partition_profile_id": str(tile_cell_key.get("partition_profile_id", "")).strip() or "geo.partition.grid_zd",
            "metric_profile_id": str(_as_map(origin.get("extensions")).get("metric_profile_id", "")).strip() or "geo.metric.euclidean",
        },
    )


def _collect_region_cell_keys(
    *,
    map_views: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None,
) -> list[dict]:
    rows = []
    for key in ("map_view", "minimap_view"):
        projected = _as_map(_as_map(_as_map(map_views).get(key)).get("projected_view_artifact"))
        for rendered in list(projected.get("rendered_cells") or []):
            row = _as_map(rendered)
            cell_key = _as_map(row.get("geo_cell_key"))
            if cell_key:
                rows.append(dict(cell_key))
    observer_cell_key = _as_map(_as_map(observer_surface_artifact).get("tile_cell_key"))
    if observer_cell_key:
        rows.append(dict(observer_cell_key))
    deduped = {}
    for row in rows:
        token = canonical_sha256(row)
        deduped[token] = dict(row)
    return [dict(deduped[key]) for key in sorted(deduped.keys())]


def build_viewer_shell_state(
    *,
    repo_root: str,
    seed: str = "",
    authority_mode: str = "dev",
    entrypoint: str = "client",
    ui_mode: str = "gui",
    start_session: bool = True,
    profile_bundle_path: str = MVP_PROFILE_BUNDLE_REL,
    pack_lock_path: str = MVP_PACK_LOCK_REL,
    perceived_model: Mapping[str, object] | None = None,
    registry_payloads: Mapping[str, object] | None = None,
    authority_context: Mapping[str, object] | None = None,
    requested_lens_profile_id: str = "",
    teleport_command: str = "",
    teleport_counter: int = 0,
    candidate_system_rows: object = None,
    inspection_snapshot: Mapping[str, object] | None = None,
    property_origin_request: Mapping[str, object] | None = None,
    property_origin_result: Mapping[str, object] | None = None,
    field_values: Mapping[str, object] | None = None,
    body_state: Mapping[str, object] | None = None,
    body_row: Mapping[str, object] | None = None,
    previous_camera_state: Mapping[str, object] | None = None,
    move_vector_local: Mapping[str, object] | None = None,
    look_vector: Mapping[str, object] | None = None,
    jump_requested: bool = False,
    toggle_lens: bool = False,
    controller_id: str = "",
    requested_debug_view_ids: object = None,
    compute_profile_id: str = "compute.default",
    map_origin_position_ref: Mapping[str, object] | None = None,
    minimap_origin_position_ref: Mapping[str, object] | None = None,
    layer_source_payloads: Mapping[str, object] | None = None,
    map_layer_ids: object = None,
    minimap_layer_ids: object = None,
    selection: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    """Build the lens-first viewer shell state without reading TruthModel directly."""

    bootstrap = build_runtime_bootstrap(
        repo_root=str(repo_root),
        entrypoint=str(entrypoint),
        ui=str(ui_mode),
        seed=str(seed),
        profile_bundle_path=str(profile_bundle_path),
        pack_lock_path=str(pack_lock_path),
        teleport="",
        authority_mode=str(authority_mode),
    )
    runtime_authority = _as_map(authority_context) or _default_authority_context(str(authority_mode))
    requested_lens = str(requested_lens_profile_id or "").strip() or str(
        _as_map(bootstrap.get("embodiment")).get("default_lens_profile_id", DEFAULT_VIEWER_LENS_PROFILE_ID)
    ).strip()
    lens_resolution = _resolve_active_lens_resolution(
        requested_lens_profile_id=requested_lens,
        authority_context=runtime_authority,
        available_lens_profile_ids=_as_map(bootstrap.get("embodiment")).get("available_lens_profile_ids"),
    )
    stage_trace = _stage_trace(
        start_session=bool(_as_bool(start_session, True)),
        seed=str(_as_map(bootstrap.get("session_spec")).get("universe_seed", "")).strip(),
        bundle_id=str(_as_map(bootstrap.get("profile_bundle")).get("profile_bundle_id", "")),
    )
    current_stage = _current_stage(stage_trace)
    current_tick = int(max(0, _as_int(_as_map(_as_map(perceived_model).get("time_state")).get("tick", 0), 0)))
    tool_requests = _tool_requests(extensions)
    teleport_tool_surface = (
        build_teleport_tool_surface(
            repo_root=str(repo_root),
            authority_context=runtime_authority,
            command=str(teleport_command),
            universe_seed=str(_as_map(bootstrap.get("session_spec")).get("universe_seed", "")).strip(),
            authority_mode=str(authority_mode),
            profile_bundle_path=str(profile_bundle_path),
            pack_lock_path=str(pack_lock_path),
            teleport_counter=int(max(0, int(teleport_counter))),
            candidate_system_rows=candidate_system_rows,
            surface_target_cell_key=_as_map(_as_map(selection).get("geo_cell_key")) or _as_map(_as_map(selection).get("tile_cell_key")),
            current_tick=int(current_tick),
        )
        if str(teleport_command or "").strip()
        else {"result": "complete", "tool_id": "tool.teleport", "teleport_plan": {"result": "complete", "process_sequence": [], "target_object_id": ""}, "process_sequence": []}
    )
    teleport_plan = dict(_as_map(teleport_tool_surface).get("teleport_plan") or {})
    if not teleport_plan:
        teleport_plan = {"result": "complete", "process_sequence": [], "target_object_id": ""}
    control_surface = _build_control_surface(
        bootstrap=bootstrap,
        authority_context=runtime_authority,
        lens_resolution=lens_resolution,
        body_state=body_state,
        body_row=body_row,
        previous_camera_state=previous_camera_state,
        controller_id=str(controller_id or "").strip(),
        move_vector_local=move_vector_local,
        look_vector=look_vector,
        jump_requested=bool(jump_requested),
        toggle_lens=bool(toggle_lens),
        requested_debug_view_ids=requested_debug_view_ids,
        compute_profile_id=str(compute_profile_id or "compute.default").strip() or "compute.default",
    )
    toolbelt_availability = build_toolbelt_availability_surface(
        authority_context=runtime_authority,
        has_physical_access=bool(selection or inspection_snapshot),
    )
    terrain_request = _as_map(tool_requests.get("terrain_edit"))
    terrain_tool_surface = {}
    terrain_kind = str(terrain_request.get("kind", "")).strip()
    if terrain_kind == "mine":
        terrain_tool_surface = build_mine_at_cursor_task(
            authority_context=runtime_authority,
            subject_id=str(terrain_request.get("subject_id", "")).strip() or str(controller_id or "").strip() or "subject.player",
            selection=selection,
            volume_amount=int(max(1, _as_int(terrain_request.get("volume_amount", 1), 1))),
            target_cell_keys=terrain_request.get("target_cell_keys"),
            geometry_edit_policy_id=str(terrain_request.get("geometry_edit_policy_id", "geo.edit.default")).strip() or "geo.edit.default",
        )
    elif terrain_kind == "fill":
        terrain_tool_surface = build_fill_at_cursor_task(
            authority_context=runtime_authority,
            subject_id=str(terrain_request.get("subject_id", "")).strip() or str(controller_id or "").strip() or "subject.player",
            selection=selection,
            volume_amount=int(max(1, _as_int(terrain_request.get("volume_amount", 1), 1))),
            material_id=str(terrain_request.get("material_id", "material.soil_fill")).strip() or "material.soil_fill",
            target_cell_keys=terrain_request.get("target_cell_keys"),
            geometry_edit_policy_id=str(terrain_request.get("geometry_edit_policy_id", "geo.edit.default")).strip() or "geo.edit.default",
        )
    elif terrain_kind == "cut":
        terrain_tool_surface = build_cut_trench_task(
            authority_context=runtime_authority,
            subject_id=str(terrain_request.get("subject_id", "")).strip() or str(controller_id or "").strip() or "subject.player",
            path_stub=terrain_request.get("path_stub"),
            volume_amount=int(max(1, _as_int(terrain_request.get("volume_amount", 1), 1))),
            selection=selection,
            geometry_edit_policy_id=str(terrain_request.get("geometry_edit_policy_id", "geo.edit.default")).strip() or "geo.edit.default",
        )
    scan_result = (
        build_scan_result(
            authority_context=runtime_authority,
            selection=selection,
            inspection_snapshot=inspection_snapshot,
            field_values=field_values,
            property_origin_result=property_origin_result,
            has_physical_access=bool(selection or inspection_snapshot),
        )
        if selection or inspection_snapshot
        else {}
    )
    logic_probe_request = _as_map(tool_requests.get("logic_probe"))
    logic_probe_surface = (
        build_logic_probe_task(
            authority_context=runtime_authority,
            subject_id=str(logic_probe_request.get("subject_id", "")).strip() or str(_as_map(selection).get("object_id", "")).strip() or "subject.logic",
            measurement_point_id=str(logic_probe_request.get("measurement_point_id", "")).strip(),
            network_id=str(logic_probe_request.get("network_id", "")).strip(),
            element_id=str(logic_probe_request.get("element_id", "")).strip(),
            port_id=str(logic_probe_request.get("port_id", "")).strip(),
        )
        if logic_probe_request
        else {}
    )
    logic_trace_request = _as_map(tool_requests.get("logic_trace"))
    logic_trace_surface = (
        build_logic_trace_task(
            authority_context=runtime_authority,
            subject_id=str(logic_trace_request.get("subject_id", "")).strip() or str(_as_map(selection).get("object_id", "")).strip() or "subject.logic",
            measurement_point_ids=logic_trace_request.get("measurement_point_ids"),
            targets=logic_trace_request.get("targets"),
            current_tick=int(current_tick),
            duration_ticks=int(max(1, _as_int(logic_trace_request.get("duration_ticks", 1), 1))),
            sampling_policy_id=str(logic_trace_request.get("sampling_policy_id", "debug.sample.default")).strip() or "debug.sample.default",
        )
        if logic_trace_request
        else {}
    )
    toolbelt_surface = {
        "result": "complete",
        "availability": dict(toolbelt_availability),
        "terrain_tool_surface": dict(terrain_tool_surface),
        "scan_result": dict(scan_result),
        "logic_probe_surface": dict(logic_probe_surface),
        "logic_trace_surface": dict(logic_trace_surface),
        "teleport_tool_surface": dict(teleport_tool_surface),
        "command_registry": {
            "commands": list(_as_map(control_surface.get("command_registry")).get("commands") or [])
            + [
                "tool mine",
                "tool fill",
                "tool cut",
                "tool scan",
                "tool probe",
                "tool trace",
                "tool tp",
            ]
        },
        "deterministic_fingerprint": "",
    }
    toolbelt_surface["deterministic_fingerprint"] = canonical_sha256(dict(toolbelt_surface, deterministic_fingerprint=""))
    observer_surface_artifact = _resolve_sky_observer_surface_artifact(
        selection=selection,
        inspection_snapshot=inspection_snapshot,
        layer_source_payloads=layer_source_payloads,
        extensions=extensions,
    )
    base_layer_source_payloads = _as_map(layer_source_payloads)
    map_origin_base = _preferred_position_ref(
        explicit_position_ref=_as_map(map_origin_position_ref) or _as_map(control_surface.get("camera_position_ref")),
        selection=selection,
    )
    minimap_origin_base = _preferred_position_ref(
        explicit_position_ref=_as_map(minimap_origin_position_ref) or _as_map(control_surface.get("camera_position_ref")),
        selection=selection,
    )
    map_origin_ref, map_surface_overrides = _surface_map_context(
        origin_position_ref=map_origin_base,
        observer_surface_artifact=observer_surface_artifact,
    )
    minimap_origin_ref, minimap_surface_overrides = _surface_map_context(
        origin_position_ref=minimap_origin_base,
        observer_surface_artifact=observer_surface_artifact,
    )
    preliminary_map_views = build_map_view_set(
        perceived_model=perceived_model,
        authority_context=runtime_authority,
        map_origin_position_ref=map_origin_ref,
        minimap_origin_position_ref=minimap_origin_ref,
        layer_source_payloads=base_layer_source_payloads,
        map_layer_ids=map_layer_ids,
        minimap_layer_ids=minimap_layer_ids,
        lens_id=str(_as_map(lens_resolution.get("lens_profile")).get("lens_id", "")).strip()
        or "lens.diegetic.sensor",
        compute_profile_id=str(compute_profile_id or "compute.default").strip() or "compute.default",
        topology_profile_id=str(map_surface_overrides.get("topology_profile_id", minimap_surface_overrides.get("topology_profile_id", "geo.topology.r3_infinite"))),
        partition_profile_id=str(map_surface_overrides.get("partition_profile_id", minimap_surface_overrides.get("partition_profile_id", "geo.partition.grid_zd"))),
        metric_profile_id=str(map_surface_overrides.get("metric_profile_id", minimap_surface_overrides.get("metric_profile_id", "geo.metric.euclidean"))),
        ui_mode=str(ui_mode),
        truth_hash_anchor=_truth_hash_anchor(perceived_model),
    )
    selection_controls = _build_selection_controls(
        selection=selection,
        map_views=preliminary_map_views,
        authority_context=runtime_authority,
    )
    sky_view_surface = build_sky_view_surface(
        universe_identity=_universe_identity_from_bootstrap(bootstrap),
        perceived_model=perceived_model,
        observer_ref=_preferred_position_ref(
            explicit_position_ref=_as_map(control_surface.get("camera_position_ref")),
            selection=selection,
        ),
        observer_surface_artifact=observer_surface_artifact,
        authority_context=runtime_authority,
        lens_profile_id=str(_as_map(lens_resolution.get("lens_profile")).get("lens_profile_id", "")).strip()
        or str(_as_map(lens_resolution.get("lens_profile")).get("lens_id", "")).strip()
        or DEFAULT_VIEWER_LENS_PROFILE_ID,
        ui_mode=str(ui_mode),
        star_artifact_rows=_worldgen_star_artifact_rows(extensions),
        planet_basic_artifact_rows=_worldgen_planet_basic_artifact_rows(extensions),
    )
    illumination_view_surface = build_lighting_view_surface(
        sky_view_artifact=_as_map(_as_map(sky_view_surface).get("sky_view_artifact")),
        observer_ref=_preferred_position_ref(
            explicit_position_ref=_as_map(control_surface.get("camera_position_ref")),
            selection=selection,
        ),
        observer_surface_artifact=observer_surface_artifact,
        ui_mode=str(ui_mode),
    )
    inspection_surfaces = build_inspection_panel_set(
        perceived_model=perceived_model,
        target_semantic_id=str(_as_map(selection).get("object_id", "")).strip()
        or str(_as_map(selection).get("target_id", "")).strip(),
        authority_context=runtime_authority,
        inspection_snapshot=inspection_snapshot,
        property_origin_request=property_origin_request,
        property_origin_result=property_origin_result,
        field_values=field_values,
        body_state=body_state,
        scan_result=scan_result,
        logic_probe_surface=logic_probe_surface,
        logic_trace_surface=logic_trace_surface,
        sky_view_artifact=_as_map(_as_map(sky_view_surface).get("sky_view_artifact")),
        illumination_view_artifact=_as_map(_as_map(illumination_view_surface).get("illumination_view_artifact")),
    )
    water_view_surface = build_water_view_surface(
        current_tick=int(current_tick),
        observer_ref=_preferred_position_ref(
            explicit_position_ref=_as_map(control_surface.get("camera_position_ref")),
            selection=selection,
        ),
        observer_surface_artifact=observer_surface_artifact,
        region_cell_keys=_collect_region_cell_keys(
            map_views=preliminary_map_views,
            observer_surface_artifact=observer_surface_artifact,
        ),
        surface_tile_artifact_rows=_resolve_water_surface_tile_artifact_rows(
            selection=selection,
            inspection_snapshot=inspection_snapshot,
            extensions=extensions,
        ),
        tide_overlay_rows=_resolve_water_tide_overlay_rows(
            selection=selection,
            inspection_snapshot=inspection_snapshot,
            field_values=field_values,
            extensions=extensions,
        ),
        ui_mode=str(ui_mode),
    )
    refinement_request_records = normalize_refinement_request_record_rows(
        list(_as_map(extensions).get("refinement_request_records") or [])
        + _viewer_generated_refinement_requests(
            preliminary_map_views=preliminary_map_views,
            observer_surface_artifact=observer_surface_artifact,
            selection=selection,
            teleport_plan=teleport_plan,
            current_tick=int(current_tick),
            extensions=extensions,
        )
    )
    refinement_status_view = build_refinement_status_view(
        region_id="region.refinement.current",
        cell_keys=_collect_region_cell_keys(
            map_views=preliminary_map_views,
            observer_surface_artifact=observer_surface_artifact,
        ),
        pending_request_rows=refinement_request_records,
        worldgen_result_rows=_as_map(extensions).get("worldgen_results"),
        refinement_cache_entries=_as_map(extensions).get("refinement_cache_entries"),
        deferred_request_rows=_as_map(extensions).get("refinement_deferred_rows"),
        extensions={
            "source": "MW4-7",
            "nonblocking": True,
            "coarse_view_visible_until_refined": True,
        },
    )
    effective_layer_source_payloads = _merge_layer_source_payloads(
        base=base_layer_source_payloads,
        extra=_merge_layer_source_payloads(
            base=build_water_layer_source_payloads(water_view_surface),
            extra=build_refinement_layer_source_payloads(refinement_status_view),
        ),
    )
    map_views = build_map_view_set(
        perceived_model=perceived_model,
        authority_context=runtime_authority,
        map_origin_position_ref=map_origin_ref,
        minimap_origin_position_ref=minimap_origin_ref,
        layer_source_payloads=effective_layer_source_payloads,
        map_layer_ids=map_layer_ids,
        minimap_layer_ids=minimap_layer_ids,
        lens_id=str(_as_map(lens_resolution.get("lens_profile")).get("lens_id", "")).strip()
        or "lens.diegetic.sensor",
        compute_profile_id=str(compute_profile_id or "compute.default").strip() or "compute.default",
        topology_profile_id=str(map_surface_overrides.get("topology_profile_id", minimap_surface_overrides.get("topology_profile_id", "geo.topology.r3_infinite"))),
        partition_profile_id=str(map_surface_overrides.get("partition_profile_id", minimap_surface_overrides.get("partition_profile_id", "geo.partition.grid_zd"))),
        metric_profile_id=str(map_surface_overrides.get("metric_profile_id", minimap_surface_overrides.get("metric_profile_id", "geo.metric.euclidean"))),
        ui_mode=str(ui_mode),
        truth_hash_anchor=_truth_hash_anchor(perceived_model),
    )
    render_contract = _render_contract(
        perceived_model=perceived_model,
        registry_payloads=registry_payloads,
        pack_lock_hash=str(_as_map(bootstrap.get("pack_lock")).get("pack_lock_hash", "")),
        camera_viewpoint_override=_as_map(control_surface.get("camera_state")),
        sky_view_artifact=_as_map(_as_map(sky_view_surface).get("sky_view_artifact")),
        illumination_view_artifact=_as_map(_as_map(illumination_view_surface).get("illumination_view_artifact")),
        water_view_artifact=_as_map(_as_map(water_view_surface).get("water_view_artifact")),
    )
    payload = {
        "result": "complete",
        "viewer_shell_id": "viewer_shell.mvp_default",
        "state_machine": {
            "states": list(stage_trace),
            "current_stage": current_stage,
            "terminal_stage": STATE_SESSION_RUNNING,
        },
        "bootstrap": dict(bootstrap),
        "authority_context": runtime_authority,
        "lens_resolution": dict(lens_resolution),
        "control_surface": dict(control_surface),
        "render_contract": render_contract,
        "teleport_plan": dict(teleport_plan),
        "toolbelt_surface": dict(toolbelt_surface),
        "inspection_surfaces": dict(inspection_surfaces),
        "map_views": dict(map_views),
        "sky_view_surface": dict(sky_view_surface),
        "illumination_view_surface": dict(illumination_view_surface),
        "water_view_surface": dict(water_view_surface),
        "refinement_surface": {
            "result": "complete",
            "request_records": [dict(row) for row in refinement_request_records],
            "status_view": dict(refinement_status_view),
            "source_kind": "derived.refinement_status_view",
            "nonblocking": True,
            "provenance_tool_id": "tool.geo.explain_property_origin",
            "selected_property_origin_request": dict(_as_map(property_origin_request)),
            "selected_property_origin_result": dict(_as_map(property_origin_result)),
        },
        "debug_overlays": {
            "terrain_collision": _terrain_debug_overlay(
                authority_context=runtime_authority,
                body_state=body_state,
                selection=selection,
            )
        },
        "selection_controls": dict(selection_controls),
        "selection": dict(selection or {}),
        "panels": _viewer_panels(current_stage),
        "ui_contract": {
            "consumes_perceived_model_only": True,
            "consumes_projection_and_lens_artifacts": True,
            "consumes_sky_view_artifacts": True,
            "consumes_illumination_view_artifacts": True,
            "consumes_water_view_artifacts": True,
            "consumes_refinement_status_view": True,
            "consumes_toolbelt_surface": True,
            "forbidden_truth_inputs": [
                "truth_model",
                "universe_state",
                "process_runtime",
            ],
            "extensions": _as_map(extensions),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload
