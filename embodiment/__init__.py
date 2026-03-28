"""Deterministic embodiment helper exports with lazy loading."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "DEFAULT_BODY_TEMPLATE_ID": ("embodiment.body", "DEFAULT_BODY_TEMPLATE_ID"),
    "body_state_rows_by_subject_id": ("embodiment.body", "body_state_rows_by_subject_id"),
    "body_template_registry_hash": ("embodiment.body", "body_template_registry_hash"),
    "body_template_rows_by_id": ("embodiment.body", "body_template_rows_by_id"),
    "build_body_state": ("embodiment.body", "build_body_state"),
    "instantiate_body_system": ("embodiment.body", "instantiate_body_system"),
    "normalize_body_state_rows": ("embodiment.body", "normalize_body_state_rows"),
    "DEFAULT_COLLISION_PROVIDER_ID": ("embodiment.collision", "DEFAULT_COLLISION_PROVIDER_ID"),
    "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID": ("embodiment.collision", "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID"),
    "collision_provider_rows_by_id": ("embodiment.collision", "collision_provider_rows_by_id"),
    "invalidate_macro_heightfield_cache_for_tiles": ("embodiment.collision", "invalidate_macro_heightfield_cache_for_tiles"),
    "movement_slope_params_rows_by_id": ("embodiment.collision", "movement_slope_params_rows_by_id"),
    "resolve_macro_heightfield_sample": ("embodiment.collision", "resolve_macro_heightfield_sample"),
    "DEFAULT_CAMERA_SMOOTHING_PARAMS_ID": ("embodiment.lens", "DEFAULT_CAMERA_SMOOTHING_PARAMS_ID"),
    "camera_smoothing_params_rows_by_id": ("embodiment.lens", "camera_smoothing_params_rows_by_id"),
    "camera_smoothing_registry_hash": ("embodiment.lens", "camera_smoothing_registry_hash"),
    "lens_profile_registry_hash": ("embodiment.lens", "lens_profile_registry_hash"),
    "lens_profile_rows_by_id": ("embodiment.lens", "lens_profile_rows_by_id"),
    "resolve_authorized_lens_profile": ("embodiment.lens", "resolve_authorized_lens_profile"),
    "resolve_lens_camera_state": ("embodiment.lens", "resolve_lens_camera_state"),
    "resolve_smoothed_camera_state": ("embodiment.lens", "resolve_smoothed_camera_state"),
    "DEFAULT_JUMP_PARAMS_ID": ("embodiment.movement", "DEFAULT_JUMP_PARAMS_ID"),
    "build_impact_event_row": ("embodiment.movement", "build_impact_event_row"),
    "build_jump_params_row": ("embodiment.movement", "build_jump_params_row"),
    "jump_params_registry_hash": ("embodiment.movement", "jump_params_registry_hash"),
    "jump_params_rows_by_id": ("embodiment.movement", "jump_params_rows_by_id"),
    "normalize_impact_event_rows": ("embodiment.movement", "normalize_impact_event_rows"),
    "normalize_jump_params_rows": ("embodiment.movement", "normalize_jump_params_rows"),
    "resolve_horizontal_damping_state": ("embodiment.movement", "resolve_horizontal_damping_state"),
    "resolve_jump_params_row": ("embodiment.movement", "resolve_jump_params_row"),
    "access_policy_registry_hash": ("embodiment.tools", "access_policy_registry_hash"),
    "access_policy_rows_by_id": ("embodiment.tools", "access_policy_rows_by_id"),
    "build_cut_trench_task": ("embodiment.tools", "build_cut_trench_task"),
    "build_fill_at_cursor_task": ("embodiment.tools", "build_fill_at_cursor_task"),
    "build_logic_probe_task": ("embodiment.tools", "build_logic_probe_task"),
    "build_logic_trace_task": ("embodiment.tools", "build_logic_trace_task"),
    "build_mine_at_cursor_task": ("embodiment.tools", "build_mine_at_cursor_task"),
    "build_scan_result": ("embodiment.tools", "build_scan_result"),
    "build_teleport_tool_surface": ("embodiment.tools", "build_teleport_tool_surface"),
    "build_tool_surface_row": ("embodiment.tools", "build_tool_surface_row"),
    "build_toolbelt_availability_surface": ("embodiment.tools", "build_toolbelt_availability_surface"),
    "entitlement_registry_hash": ("embodiment.tools", "entitlement_registry_hash"),
    "entitlement_rows_by_id": ("embodiment.tools", "entitlement_rows_by_id"),
    "evaluate_tool_access": ("embodiment.tools", "evaluate_tool_access"),
    "tool_capability_registry_hash": ("embodiment.tools", "tool_capability_registry_hash"),
    "tool_capability_rows_by_id": ("embodiment.tools", "tool_capability_rows_by_id"),
}

__all__ = sorted(_EXPORTS.keys())


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError("module 'embodiment' has no attribute {!r}".format(name))
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(__all__))
