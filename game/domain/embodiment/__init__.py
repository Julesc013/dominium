"""Deterministic embodiment helper exports with lazy loading."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "DEFAULT_BODY_TEMPLATE_ID": (".body", "DEFAULT_BODY_TEMPLATE_ID"),
    "body_state_rows_by_subject_id": (".body", "body_state_rows_by_subject_id"),
    "body_template_registry_hash": (".body", "body_template_registry_hash"),
    "body_template_rows_by_id": (".body", "body_template_rows_by_id"),
    "build_body_state": (".body", "build_body_state"),
    "instantiate_body_system": (".body", "instantiate_body_system"),
    "normalize_body_state_rows": (".body", "normalize_body_state_rows"),
    "DEFAULT_COLLISION_PROVIDER_ID": (".collision", "DEFAULT_COLLISION_PROVIDER_ID"),
    "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID": (".collision", "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID"),
    "collision_provider_rows_by_id": (".collision", "collision_provider_rows_by_id"),
    "invalidate_macro_heightfield_cache_for_tiles": (".collision", "invalidate_macro_heightfield_cache_for_tiles"),
    "movement_slope_params_rows_by_id": (".collision", "movement_slope_params_rows_by_id"),
    "resolve_macro_heightfield_sample": (".collision", "resolve_macro_heightfield_sample"),
    "DEFAULT_CAMERA_SMOOTHING_PARAMS_ID": (".lens", "DEFAULT_CAMERA_SMOOTHING_PARAMS_ID"),
    "camera_smoothing_params_rows_by_id": (".lens", "camera_smoothing_params_rows_by_id"),
    "camera_smoothing_registry_hash": (".lens", "camera_smoothing_registry_hash"),
    "lens_profile_registry_hash": (".lens", "lens_profile_registry_hash"),
    "lens_profile_rows_by_id": (".lens", "lens_profile_rows_by_id"),
    "resolve_authorized_lens_profile": (".lens", "resolve_authorized_lens_profile"),
    "resolve_lens_camera_state": (".lens", "resolve_lens_camera_state"),
    "resolve_smoothed_camera_state": (".lens", "resolve_smoothed_camera_state"),
    "DEFAULT_JUMP_PARAMS_ID": (".movement", "DEFAULT_JUMP_PARAMS_ID"),
    "build_impact_event_row": (".movement", "build_impact_event_row"),
    "build_jump_params_row": (".movement", "build_jump_params_row"),
    "jump_params_registry_hash": (".movement", "jump_params_registry_hash"),
    "jump_params_rows_by_id": (".movement", "jump_params_rows_by_id"),
    "normalize_impact_event_rows": (".movement", "normalize_impact_event_rows"),
    "normalize_jump_params_rows": (".movement", "normalize_jump_params_rows"),
    "resolve_horizontal_damping_state": (".movement", "resolve_horizontal_damping_state"),
    "resolve_jump_params_row": (".movement", "resolve_jump_params_row"),
    "access_policy_registry_hash": (".tools", "access_policy_registry_hash"),
    "access_policy_rows_by_id": (".tools", "access_policy_rows_by_id"),
    "build_cut_trench_task": (".tools", "build_cut_trench_task"),
    "build_fill_at_cursor_task": (".tools", "build_fill_at_cursor_task"),
    "build_logic_probe_task": (".tools", "build_logic_probe_task"),
    "build_logic_trace_task": (".tools", "build_logic_trace_task"),
    "build_mine_at_cursor_task": (".tools", "build_mine_at_cursor_task"),
    "build_scan_result": (".tools", "build_scan_result"),
    "build_teleport_tool_surface": (".tools", "build_teleport_tool_surface"),
    "build_tool_surface_row": (".tools", "build_tool_surface_row"),
    "build_toolbelt_availability_surface": (".tools", "build_toolbelt_availability_surface"),
    "entitlement_registry_hash": (".tools", "entitlement_registry_hash"),
    "entitlement_rows_by_id": (".tools", "entitlement_rows_by_id"),
    "evaluate_tool_access": (".tools", "evaluate_tool_access"),
    "tool_capability_registry_hash": (".tools", "tool_capability_registry_hash"),
    "tool_capability_rows_by_id": (".tools", "tool_capability_rows_by_id"),
}

__all__ = sorted(_EXPORTS.keys())


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))
    module_name, attr_name = target
    module = import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(__all__))
