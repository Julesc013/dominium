"""Platform abstraction surfaces for client presentation/runtime integration."""

from .platform_audio import close_audio_device, create_audio_device, submit_audio_frame
from .platform_probe import (
    canonical_platform_id,
    load_platform_capability_registry,
    platform_capability_rows_by_id,
    platform_family_id,
    PLATFORM_ID_ORDER,
    probe_platform_descriptor,
    project_feature_capabilities_for_platform,
)
from .target_matrix import (
    TARGET_MATRIX_REGISTRY_REL,
    load_target_matrix_registry,
    release_index_target_rows,
    select_target_matrix_row,
    target_matrix_registry_hash,
    target_matrix_rows_by_id,
)
from .platform_gfx import (
    create_graphics_context,
    destroy_graphics_context,
    list_available_backends,
    present_frame,
    resize_graphics_surface,
)
from .platform_input import (
    create_keyboard_event,
    create_mouse_event,
    normalize_input_event,
    queue_input_event,
)
from .platform_input_routing import pick_render_model_target, route_platform_events_to_commands
from .platform_caps_probe import probe_platform_caps
from .platform_window import close_window, create_window, detect_platform_id, resize_window

__all__ = [
    "close_audio_device",
    "close_window",
    "canonical_platform_id",
    "create_audio_device",
    "create_graphics_context",
    "create_keyboard_event",
    "create_mouse_event",
    "create_window",
    "detect_platform_id",
    "destroy_graphics_context",
    "list_available_backends",
    "load_platform_capability_registry",
    "normalize_input_event",
    "platform_capability_rows_by_id",
    "platform_family_id",
    "PLATFORM_ID_ORDER",
    "pick_render_model_target",
    "probe_platform_descriptor",
    "present_frame",
    "probe_platform_caps",
    "project_feature_capabilities_for_platform",
    "queue_input_event",
    "resize_graphics_surface",
    "resize_window",
    "route_platform_events_to_commands",
    "TARGET_MATRIX_REGISTRY_REL",
    "load_target_matrix_registry",
    "release_index_target_rows",
    "submit_audio_frame",
    "select_target_matrix_row",
    "target_matrix_registry_hash",
    "target_matrix_rows_by_id",
]
