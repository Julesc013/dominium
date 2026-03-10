"""Deterministic EMB-2 locomotion polish probes for replay and TestX reuse."""

from __future__ import annotations

import copy
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.client.ui.viewer_shell import build_viewer_shell_state  # noqa: E402
from src.embodiment import lens_profile_rows_by_id, resolve_smoothed_camera_state  # noqa: E402
from tools.embodiment.earth6_probe import build_collision_fixture  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import execute_intent, replay_intent_script  # noqa: E402
from tools.xstack.testx.tests.emb0_testlib import authority_context, law_profile, policy_context, seed_embodied_state  # noqa: E402


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _contexts(
    *,
    law_allows_jump: bool,
    authority_has_jump: bool | None = None,
    include_tick: bool = True,
) -> tuple[dict, dict, dict]:
    allowed_processes = ["process.body_apply_input"]
    entitlements = ["entitlement.control.possess"]
    if include_tick:
        allowed_processes.append("process.body_tick")
    if law_allows_jump:
        allowed_processes.append("process.body_jump")
    if authority_has_jump is None:
        authority_has_jump = bool(law_allows_jump)
    if authority_has_jump:
        entitlements.append("ent.move.jump")
    return (
        copy.deepcopy(law_profile(allowed_processes)),
        copy.deepcopy(authority_context(entitlements, privilege_level="operator")),
        copy.deepcopy(policy_context()),
    )


def _execute(
    *,
    state: dict,
    process_id: str,
    inputs: Mapping[str, object],
    law_allows_jump: bool,
    authority_has_jump: bool | None = None,
    include_tick: bool = True,
    intent_suffix: str = "001",
) -> dict:
    law, auth, policy = _contexts(
        law_allows_jump=law_allows_jump,
        authority_has_jump=authority_has_jump,
        include_tick=include_tick,
    )
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.emb2.{}.{}".format(process_id.replace(".", "_"), intent_suffix),
            "process_id": process_id,
            "inputs": dict(inputs),
        },
        law_profile=law,
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )


def _prepare_grounded_state() -> dict:
    state = build_collision_fixture(body_z=120)
    grounded_tick = _execute(
        state=state,
        process_id="process.body_tick",
        inputs={"body_id": "body.emb.test", "dt_ticks": 1},
        law_allows_jump=True,
        authority_has_jump=True,
        include_tick=True,
        intent_suffix="ground",
    )
    if str(grounded_tick.get("result", "")).strip() != "complete":
        return state
    return state


def jump_entitlement_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    state = build_collision_fixture(body_z=120)
    grounded_tick = _execute(
        state=state,
        process_id="process.body_tick",
        inputs={"body_id": "body.emb.test", "dt_ticks": 1},
        law_allows_jump=True,
        authority_has_jump=False,
        include_tick=True,
        intent_suffix="ground",
    )
    jump = _execute(
        state=state,
        process_id="process.body_jump",
        inputs={"body_id": "body.emb.test", "controller_id": "controller.emb.test", "dt_ticks": 1},
        law_allows_jump=True,
        authority_has_jump=False,
        include_tick=True,
        intent_suffix="jump",
    )
    refusal_row = _as_map(jump.get("refusal"))
    return {
        "result": "complete"
        if str(grounded_tick.get("result", "")).strip() == "complete" and str(jump.get("result", "")).strip() == "refused"
        else "violation",
        "ground_tick_result": str(grounded_tick.get("result", "")).strip(),
        "jump_result": str(jump.get("result", "")).strip(),
        "reason_code": str(refusal_row.get("reason_code", "")).strip(),
        "required_entitlement_id": "ent.move.jump",
        "deterministic_fingerprint": canonical_sha256(
            {
                "ground_tick_result": str(grounded_tick.get("result", "")).strip(),
                "jump_result": str(jump.get("result", "")).strip(),
                "reason_code": str(refusal_row.get("reason_code", "")).strip(),
            }
        ),
    }


def jump_grounded_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    airborne_state = build_collision_fixture(body_z=2400)
    airborne_jump = _execute(
        state=airborne_state,
        process_id="process.body_jump",
        inputs={"body_id": "body.emb.test", "controller_id": "controller.emb.test", "dt_ticks": 1},
        law_allows_jump=True,
        authority_has_jump=True,
        include_tick=True,
        intent_suffix="airborne",
    )
    grounded_state = _prepare_grounded_state()
    grounded_jump = _execute(
        state=grounded_state,
        process_id="process.body_jump",
        inputs={"body_id": "body.emb.test", "controller_id": "controller.emb.test", "dt_ticks": 1},
        law_allows_jump=True,
        authority_has_jump=True,
        include_tick=True,
        intent_suffix="grounded",
    )
    grounded_body = dict(list(grounded_state.get("body_assemblies") or [])[0] or {})
    locomotion_state = _as_map(_as_map(grounded_body.get("extensions")).get("locomotion_state"))
    collision_state = _as_map(_as_map(grounded_body.get("extensions")).get("terrain_collision_state"))
    refusal_row = _as_map(airborne_jump.get("refusal"))
    return {
        "result": "complete"
        if str(airborne_jump.get("result", "")).strip() == "refused" and str(grounded_jump.get("result", "")).strip() == "complete"
        else "violation",
        "airborne_result": str(airborne_jump.get("result", "")).strip(),
        "airborne_reason_code": str(refusal_row.get("reason_code", "")).strip(),
        "grounded_result": str(grounded_jump.get("result", "")).strip(),
        "velocity_z_after_jump": int(_as_map(grounded_body.get("velocity_mm_per_tick")).get("z", 0) or 0),
        "grounded_after_jump": bool(collision_state.get("grounded", False)),
        "cooldown_remaining_ticks": int(locomotion_state.get("jump_cooldown_remaining_ticks", 0) or 0),
        "last_jump_tick": int(locomotion_state.get("last_jump_tick", 0) or 0),
        "deterministic_fingerprint": canonical_sha256(
            {
                "airborne_result": str(airborne_jump.get("result", "")).strip(),
                "airborne_reason_code": str(refusal_row.get("reason_code", "")).strip(),
                "grounded_result": str(grounded_jump.get("result", "")).strip(),
                "velocity_z_after_jump": int(_as_map(grounded_body.get("velocity_mm_per_tick")).get("z", 0) or 0),
                "grounded_after_jump": bool(collision_state.get("grounded", False)),
                "cooldown_remaining_ticks": int(locomotion_state.get("jump_cooldown_remaining_ticks", 0) or 0),
            }
        ),
    }


def impact_event_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    state = build_collision_fixture(body_z=120)
    body = dict(list(state.get("body_assemblies") or [])[0] or {})
    body["velocity_mm_per_tick"] = {"x": 0, "y": 0, "z": -400}
    body_rows = list(state.get("body_assemblies") or [])
    body_rows[0] = body
    state["body_assemblies"] = body_rows
    momentum = dict(list(state.get("momentum_states") or [])[0] or {})
    mass_value = int(max(1, _as_int(momentum.get("mass_value", 5), 5)))
    momentum["momentum_linear"] = {"x": 0, "y": 0, "z": -400 * int(mass_value)}
    momentum_rows = list(state.get("momentum_states") or [])
    momentum_rows[0] = momentum
    state["momentum_states"] = momentum_rows
    tick = _execute(
        state=state,
        process_id="process.body_tick",
        inputs={"body_id": "body.emb.test", "dt_ticks": 1},
        law_allows_jump=True,
        authority_has_jump=True,
        include_tick=True,
        intent_suffix="impact",
    )
    impact_events = list(state.get("impact_events") or [])
    impact_event = dict(impact_events[0] or {}) if impact_events else {}
    grounded_body = dict(list(state.get("body_assemblies") or [])[0] or {})
    locomotion_state = _as_map(_as_map(grounded_body.get("extensions")).get("locomotion_state"))
    explain_artifact = _as_map(tick.get("impact_explain_artifact"))
    return {
        "result": "complete"
        if str(tick.get("result", "")).strip() == "complete" and bool(impact_event)
        else "violation",
        "impact_event_id": str(impact_event.get("event_id", "")).strip(),
        "impact_speed": int(impact_event.get("impact_speed", 0) or 0),
        "impact_event_hash_chain": str(state.get("impact_event_hash_chain", "")).strip(),
        "last_impact_speed": int(locomotion_state.get("last_impact_speed", 0) or 0),
        "impact_explain_id": str(explain_artifact.get("explain_id", "")).strip(),
        "deterministic_fingerprint": canonical_sha256(
            {
                "impact_event_id": str(impact_event.get("event_id", "")).strip(),
                "impact_speed": int(impact_event.get("impact_speed", 0) or 0),
                "impact_event_hash_chain": str(state.get("impact_event_hash_chain", "")).strip(),
                "impact_explain_id": str(explain_artifact.get("explain_id", "")).strip(),
            }
        ),
    }


def camera_smoothing_report(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    target_camera_state = {
        "position_mm": {"x": 9600, "y": -3200, "z": 4200},
        "orientation_mdeg": {"yaw": 12000, "pitch": -800, "roll": 0},
        "view_mode_id": "view.third_person.player",
        "view_policy_id": "view.third_person_diegetic",
        "lens_id": "lens.diegetic.sensor",
        "requires_embodiment": True,
    }
    previous_camera_state = {
        "position_mm": {"x": 0, "y": 0, "z": 1600},
        "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        "view_mode_id": "view.third_person.player",
        "view_policy_id": "view.third_person_diegetic",
        "lens_id": "lens.diegetic.sensor",
        "requires_embodiment": True,
    }
    lens_profile_row = dict(lens_profile_rows_by_id().get("lens.tp") or {})
    first = resolve_smoothed_camera_state(
        target_camera_state=copy.deepcopy(target_camera_state),
        previous_camera_state=copy.deepcopy(previous_camera_state),
        lens_profile_row=lens_profile_row,
    )
    second = resolve_smoothed_camera_state(
        target_camera_state=copy.deepcopy(target_camera_state),
        previous_camera_state=copy.deepcopy(previous_camera_state),
        lens_profile_row=lens_profile_row,
    )
    viewer_seed = seed_embodied_state(include_camera=True)
    original_body = copy.deepcopy(dict(viewer_seed["body_assemblies"][0]))
    original_body_state = copy.deepcopy(dict(viewer_seed["body_states"][0]))
    shell_state = build_viewer_shell_state(
        repo_root=repo_root,
        seed="0",
        authority_mode="dev",
        entrypoint="client",
        ui_mode="gui",
        start_session=True,
        perceived_model={"time_state": {"tick": 4}},
        requested_lens_profile_id="lens.tp",
        body_state=copy.deepcopy(original_body_state),
        body_row=copy.deepcopy(original_body),
        previous_camera_state=copy.deepcopy(previous_camera_state),
        controller_id="controller.emb.test",
    )
    control_surface = _as_map(shell_state.get("control_surface"))
    smoothed_state = _as_map(control_surface.get("camera_state"))
    target_state = _as_map(control_surface.get("camera_target_state"))
    body_unchanged = original_body == dict(viewer_seed["body_assemblies"][0]) and original_body_state == dict(viewer_seed["body_states"][0])
    return {
        "result": "complete"
        if dict(first) == dict(second)
        and bool(first.get("smoothing_applied", False))
        and _as_map(first.get("camera_state")).get("position_mm") != _as_map(target_camera_state).get("position_mm")
        and smoothed_state != target_state
        and body_unchanged
        else "violation",
        "smoothing_applied": bool(first.get("smoothing_applied", False)),
        "camera_smoothing_params_id": str(first.get("camera_smoothing_params_id", "")).strip(),
        "smoothed_position_mm": dict(_as_map(first.get("camera_state")).get("position_mm") or {}),
        "target_position_mm": dict(_as_map(target_camera_state).get("position_mm") or {}),
        "viewer_render_camera_position_mm": dict(smoothed_state.get("position_mm") or {}),
        "viewer_target_camera_position_mm": dict(target_state.get("position_mm") or {}),
        "body_unchanged": bool(body_unchanged),
        "deterministic_fingerprint": canonical_sha256(
            {
                "smoothing_applied": bool(first.get("smoothing_applied", False)),
                "camera_smoothing_params_id": str(first.get("camera_smoothing_params_id", "")).strip(),
                "smoothed_position_mm": dict(_as_map(first.get("camera_state")).get("position_mm") or {}),
                "viewer_render_camera_position_mm": dict(smoothed_state.get("position_mm") or {}),
                "viewer_target_camera_position_mm": dict(target_state.get("position_mm") or {}),
                "body_unchanged": bool(body_unchanged),
            }
        ),
    }


def verify_locomotion_window_replay(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    fixture = build_collision_fixture(body_z=120, gravity_vector={"x": 0, "y": 0, "z": -12})
    intents = [
        {
            "intent_id": "intent.emb2.body_tick.ground",
            "process_id": "process.body_tick",
            "inputs": {"body_id": "body.emb.test", "dt_ticks": 1},
        },
        {
            "intent_id": "intent.emb2.body_jump.001",
            "process_id": "process.body_jump",
            "inputs": {"body_id": "body.emb.test", "controller_id": "controller.emb.test", "dt_ticks": 1},
        },
    ]
    for tick_index in range(1, 19):
        intents.append(
            {
                "intent_id": "intent.emb2.body_tick.air.{}".format(tick_index),
                "process_id": "process.body_tick",
                "inputs": {"body_id": "body.emb.test", "dt_ticks": 1},
            }
        )
    law, auth, policy = _contexts(law_allows_jump=True, authority_has_jump=True, include_tick=True)
    first = replay_intent_script(
        universe_state=copy.deepcopy(fixture),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        intents=copy.deepcopy(intents),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = replay_intent_script(
        universe_state=copy.deepcopy(fixture),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        intents=copy.deepcopy(intents),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    first_state = _as_map(first.get("universe_state"))
    stable = (
        str(first.get("result", "")).strip() == "complete"
        and str(second.get("result", "")).strip() == "complete"
        and str(first.get("final_state_hash", "")).strip() == str(second.get("final_state_hash", "")).strip()
    )
    impact_events = list(first_state.get("impact_events") or [])
    return {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "final_state_hash": str(first.get("final_state_hash", "")).strip(),
        "impact_event_hash_chain": str(first_state.get("impact_event_hash_chain", "")).strip(),
        "impact_event_count": int(len(impact_events)),
        "impulse_event_hash_chain": str(first_state.get("impulse_event_hash_chain", "")).strip(),
        "deterministic_fingerprint": canonical_sha256(
            {
                "stable_across_repeated_runs": bool(stable),
                "final_state_hash": str(first.get("final_state_hash", "")).strip(),
                "impact_event_hash_chain": str(first_state.get("impact_event_hash_chain", "")).strip(),
                "impact_event_count": int(len(impact_events)),
            }
        ),
    }


def locomotion_hash(repo_root: str) -> str:
    _ensure_repo_root(repo_root)
    return canonical_sha256(
        {
            "jump_entitlement": jump_entitlement_report(repo_root),
            "jump_grounded": jump_grounded_report(repo_root),
            "impact_event": impact_event_report(repo_root),
            "camera_smoothing": camera_smoothing_report(repo_root),
            "replay": verify_locomotion_window_replay(repo_root),
        }
    )


__all__ = [
    "camera_smoothing_report",
    "impact_event_report",
    "jump_entitlement_report",
    "jump_grounded_report",
    "locomotion_hash",
    "verify_locomotion_window_replay",
]
