"""Deterministic UX-0 viewer shell state machine over derived artifacts only."""

from __future__ import annotations

from typing import Mapping

from src.client.render import build_render_model
from src.embodiment import resolve_authorized_lens_profile
from src.client.ui.inspect_panels import build_inspection_panel_set
from src.client.ui.teleport_controller import build_teleport_plan
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


def _sorted_strings(values: object) -> list[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _default_authority_context(authority_mode: str) -> dict:
    mode = str(authority_mode or "").strip().lower() or "dev"
    entitlements = ["session.boot", "entitlement.control.camera"]
    if mode == "dev":
        entitlements.extend(
            [
                "lens.nondiegetic.access",
                "entitlement.control.lens_override",
                "entitlement.inspect",
                "entitlement.debug_view",
                "entitlement.teleport",
                "entitlement.observer.truth",
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
) -> dict:
    perceived = _as_map(perceived_model)
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
    )
    return {
        "result": str(render_result.get("result", "")) or "complete",
        "render_model": dict(render_result.get("render_model") or {}),
        "render_model_hash": str(render_result.get("render_model_hash", "")).strip(),
        "source_kind": "perceived.render_model",
    }


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
    lens_resolution = resolve_authorized_lens_profile(
        requested_lens_profile_id=requested_lens,
        authority_context=runtime_authority,
    )
    stage_trace = _stage_trace(
        start_session=bool(_as_bool(start_session, True)),
        seed=str(_as_map(bootstrap.get("session_spec")).get("universe_seed", "")).strip(),
        bundle_id=str(_as_map(bootstrap.get("profile_bundle")).get("profile_bundle_id", "")),
    )
    current_stage = _current_stage(stage_trace)
    render_contract = _render_contract(
        perceived_model=perceived_model,
        registry_payloads=registry_payloads,
        pack_lock_hash=str(_as_map(bootstrap.get("pack_lock")).get("pack_lock_hash", "")),
    )
    teleport_plan = (
        build_teleport_plan(
            repo_root=str(repo_root),
            command=str(teleport_command),
            universe_seed=str(_as_map(bootstrap.get("session_spec")).get("universe_seed", "")).strip(),
            authority_mode=str(authority_mode),
            profile_bundle_path=str(profile_bundle_path),
            pack_lock_path=str(pack_lock_path),
            teleport_counter=int(max(0, int(teleport_counter))),
            candidate_system_rows=candidate_system_rows,
        )
        if str(teleport_command or "").strip()
        else {"result": "complete", "process_sequence": [], "target_object_id": ""}
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
        "render_contract": render_contract,
        "teleport_plan": dict(teleport_plan),
        "inspection_surfaces": dict(inspection_surfaces),
        "selection": dict(selection or {}),
        "panels": _viewer_panels(current_stage),
        "ui_contract": {
            "consumes_perceived_model_only": True,
            "consumes_projection_and_lens_artifacts": True,
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
