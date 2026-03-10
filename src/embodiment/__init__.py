"""Deterministic embodiment helper exports with lazy loading."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "DEFAULT_BODY_TEMPLATE_ID": ("src.embodiment.body", "DEFAULT_BODY_TEMPLATE_ID"),
    "body_state_rows_by_subject_id": ("src.embodiment.body", "body_state_rows_by_subject_id"),
    "body_template_registry_hash": ("src.embodiment.body", "body_template_registry_hash"),
    "body_template_rows_by_id": ("src.embodiment.body", "body_template_rows_by_id"),
    "build_body_state": ("src.embodiment.body", "build_body_state"),
    "instantiate_body_system": ("src.embodiment.body", "instantiate_body_system"),
    "normalize_body_state_rows": ("src.embodiment.body", "normalize_body_state_rows"),
    "DEFAULT_COLLISION_PROVIDER_ID": ("src.embodiment.collision", "DEFAULT_COLLISION_PROVIDER_ID"),
    "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID": ("src.embodiment.collision", "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID"),
    "collision_provider_rows_by_id": ("src.embodiment.collision", "collision_provider_rows_by_id"),
    "invalidate_macro_heightfield_cache_for_tiles": ("src.embodiment.collision", "invalidate_macro_heightfield_cache_for_tiles"),
    "movement_slope_params_rows_by_id": ("src.embodiment.collision", "movement_slope_params_rows_by_id"),
    "resolve_macro_heightfield_sample": ("src.embodiment.collision", "resolve_macro_heightfield_sample"),
    "DEFAULT_CAMERA_SMOOTHING_PARAMS_ID": ("src.embodiment.lens", "DEFAULT_CAMERA_SMOOTHING_PARAMS_ID"),
    "camera_smoothing_params_rows_by_id": ("src.embodiment.lens", "camera_smoothing_params_rows_by_id"),
    "camera_smoothing_registry_hash": ("src.embodiment.lens", "camera_smoothing_registry_hash"),
    "lens_profile_registry_hash": ("src.embodiment.lens", "lens_profile_registry_hash"),
    "lens_profile_rows_by_id": ("src.embodiment.lens", "lens_profile_rows_by_id"),
    "resolve_authorized_lens_profile": ("src.embodiment.lens", "resolve_authorized_lens_profile"),
    "resolve_lens_camera_state": ("src.embodiment.lens", "resolve_lens_camera_state"),
    "resolve_smoothed_camera_state": ("src.embodiment.lens", "resolve_smoothed_camera_state"),
    "DEFAULT_JUMP_PARAMS_ID": ("src.embodiment.movement", "DEFAULT_JUMP_PARAMS_ID"),
    "build_impact_event_row": ("src.embodiment.movement", "build_impact_event_row"),
    "build_jump_params_row": ("src.embodiment.movement", "build_jump_params_row"),
    "jump_params_registry_hash": ("src.embodiment.movement", "jump_params_registry_hash"),
    "jump_params_rows_by_id": ("src.embodiment.movement", "jump_params_rows_by_id"),
    "normalize_impact_event_rows": ("src.embodiment.movement", "normalize_impact_event_rows"),
    "normalize_jump_params_rows": ("src.embodiment.movement", "normalize_jump_params_rows"),
    "resolve_horizontal_damping_state": ("src.embodiment.movement", "resolve_horizontal_damping_state"),
    "resolve_jump_params_row": ("src.embodiment.movement", "resolve_jump_params_row"),
    "access_policy_registry_hash": ("src.embodiment.tools", "access_policy_registry_hash"),
    "access_policy_rows_by_id": ("src.embodiment.tools", "access_policy_rows_by_id"),
    "build_cut_trench_task": ("src.embodiment.tools", "build_cut_trench_task"),
    "build_fill_at_cursor_task": ("src.embodiment.tools", "build_fill_at_cursor_task"),
    "build_logic_probe_task": ("src.embodiment.tools", "build_logic_probe_task"),
    "build_logic_trace_task": ("src.embodiment.tools", "build_logic_trace_task"),
    "build_mine_at_cursor_task": ("src.embodiment.tools", "build_mine_at_cursor_task"),
    "build_scan_result": ("src.embodiment.tools", "build_scan_result"),
    "build_teleport_tool_surface": ("src.embodiment.tools", "build_teleport_tool_surface"),
    "build_tool_surface_row": ("src.embodiment.tools", "build_tool_surface_row"),
    "build_toolbelt_availability_surface": ("src.embodiment.tools", "build_toolbelt_availability_surface"),
    "entitlement_registry_hash": ("src.embodiment.tools", "entitlement_registry_hash"),
    "entitlement_rows_by_id": ("src.embodiment.tools", "entitlement_rows_by_id"),
    "evaluate_tool_access": ("src.embodiment.tools", "evaluate_tool_access"),
    "tool_capability_registry_hash": ("src.embodiment.tools", "tool_capability_registry_hash"),
    "tool_capability_rows_by_id": ("src.embodiment.tools", "tool_capability_rows_by_id"),
}

__all__ = sorted(_EXPORTS.keys())


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError("module 'src.embodiment' has no attribute {!r}".format(name))
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(__all__))
